#!/usr/bin/env python

###############################################################################
# Copyright 2015-2021 University of Florida. All rights reserved.
# This file is part of UF CTS-IT's NACCulator project.
# Use of this source code is governed by the license found in the LICENSE file.
###############################################################################

import argparse
import csv
import re
import sys
import traceback
import typing

from nacc.uds3 import blanks as blanks_uds3
from nacc.lbd import blanks as blanks_lbd
from nacc.ftld import blanks as blanks_ftld
from nacc.csf import blanks as blanks_csf
from nacc.cv import blanks as blanks_cv
from nacc.uds3.ivp import builder as ivp_builder
from nacc.uds3.np import builder as np_builder
from nacc.uds3.fvp import builder as fvp_builder
from nacc.uds3.tfp import builder as tfp_builder
from nacc.uds3.tfp.v3_2 import builder as tfp_new_builder
from nacc.uds3.m import builder as m_builder
from nacc.lbd.ivp import builder as lbd_ivp_builder
from nacc.lbd.fvp import builder as lbd_fvp_builder
from nacc.lbd.v3_1.ivp import builder as lbd_short_ivp_builder
from nacc.lbd.v3_1.fvp import builder as lbd_short_fvp_builder
from nacc.ftld.ivp import builder as ftld_ivp_builder
from nacc.ftld.fvp import builder as ftld_fvp_builder
from nacc.csf import builder as csf_builder
from nacc.cv import builder as cv_builder
from nacc.uds3 import filters
from nacc.uds3 import packet as uds3_packet
from nacc.uds3 import Field


def check_blanks(packet: uds3_packet.Packet, options: argparse.Namespace) \
        -> typing.List:
    """
    Parses rules for when each field should be blank and then checks them
    """
    warnings: list = []

    for form in packet:
        # Find all fields that:
        #   1) have blanking rules; and
        #   2) aren't blank.
        formid = ""
        try:
            formid = " in form %s" % (form.fields['FORMID'].value)
        except KeyError:
            pass
        for field in [f for f in form.fields.values()
                      if f.blanks and not empty(f)]:

            for rule in field.blanks:
                if not options.lbd and not options.ftld and not options.csf \
                   and not options.cv:
                    r = blanks_uds3.convert_rule_to_python(field.name, rule)
                    if r(packet):
                        blank_warnings(warnings, field.name, formid,
                                       field.value, len(field.value), rule)

                if options.lbd:
                    t = blanks_lbd.convert_rule_to_python(field.name, rule)
                    if t(packet):
                        blank_warnings(warnings, field.name, formid,
                                       field.value, len(field.value), rule)

                if options.ftld:
                    s = blanks_ftld.convert_rule_to_python(field.name, rule)
                    if s(packet):
                        blank_warnings(warnings, field.name, formid,
                                       field.value, len(field.value), rule)

                if options.csf:
                    q = blanks_csf.convert_rule_to_python(field.name, rule)
                    if q(packet):
                        blank_warnings(warnings, field.name, formid,
                                       field.value, len(field.value), rule)

                if options.cv:
                    u = blanks_cv.convert_rule_to_python(field.name, rule)
                    if u(packet):
                        blank_warnings(warnings, field.name, formid,
                                       field.value, len(field.value), rule)
    return warnings


def blank_warnings(warnings, fieldname, formid, value, length, rule):
    warnings.append(
        "%s%s is '%s' with length '%s', but should be blank: '%s'." %
        (fieldname, formid, value, length, rule))
    return warnings


def check_characters(packet: uds3_packet.Packet) -> typing.List:
    """
    Checks typename="Char" fields for any of 4 special characters: & ' " %
    If these characters are found, throws an error and skips the ptid
    """
    warnings = []

    for form in packet:
        # Find all fields that have any of the forbidden characters, and
        #   figure out which characters are present in the string.
        # If they are found, append an error to our error file
        #   and skip the PTID
        for field in [f for f in form.fields.values()]:
            if field.typename == "Char":
                incompatible = check_for_bad_characters(field)

                if incompatible:
                    character = " ".join(incompatible)
                    formid = ""
                    try:
                        formid = " in form %s" % (form.fields['FORMID'].value)
                    except KeyError:
                        pass
                    warnings.append(
                        '%s%s is \'%s\', which has invalid character(s) %s .'
                        ' This field can have any text or numbers, but cannot'
                        ' include single quotes \', double quotes \",'
                        ' ampersands & or percentage signs %% ' %
                        (field.name, formid, field.value, character))

    return warnings


def check_for_bad_characters(field: Field) -> typing.List:
    """
    Searches the flagged fields for the special characters
    and tallies up all instances of each character
    """
    incompatible: list = []

    text = field.value
    chars = ["'", '"', '&', '%']

    if any((c in chars) for c in text):
        quote = re.search("'", text)
        num_quote = text.count("'")
        dquote = re.search('"', text)
        num_dquote = text.count('"')
        amp = re.search('&', text)
        num_amp = text.count("&")
        percent = re.search('%', text)
        num_percent = text.count("%")

        incompatible = []
        if quote:
            quote_char = "'"
            incompatible.append(quote_char + " (%s)" % num_quote)
        if dquote:
            dquote_char = '"'
            incompatible.append(dquote_char + " (%s)" % num_dquote)
        if amp:
            amp_char = '&'
            incompatible.append(amp_char + " (%s)" % num_amp)
        if percent:
            percent_char = '%'
            incompatible.append(percent_char + " (%s)" % num_percent)

    return incompatible


def check_redcap_event(options, record, out=sys.stdout, err=sys.stderr) -> bool:
    """
    Determines if the record's redcap_event_name and filled forms match the
    options flag
    """
    if options.lbd and options.ivp:
        event_name = 'initial'
        try:
            form_match_lbd = record['lbd_ivp_b1l_complete']
        except KeyError:
            form_match_lbd = record['lbd_ivp_b1l_clinical_symptoms_and_exam_complete']
        if form_match_lbd in ['0', '']:
            return False
    elif options.lbd and options.fvp:
        event_name = 'follow'
        try:
            form_match_lbd = record['lbd_fvp_b1l_complete']
        except KeyError:
            form_match_lbd = record['lbd_fvp_b1l_clinical_symptoms_and_exam_complete']
        if form_match_lbd in ['0', '']:
            return False
    elif options.lbdsv and options.ivp:
        event_name = 'initial'
        try:
            form_match_lbd = record['lbd_ivp_b1l_complete']
        except KeyError:
            form_match_lbd = record['lbd_ivp_b1l_clinical_symptoms_and_exam_complete']
        if form_match_lbd in ['0', '']:
            return False
    elif options.lbdsv and options.fvp:
        event_name = 'follow'
        try:
            form_match_lbd = record['lbd_fvp_b1l_complete']
        except KeyError:
            form_match_lbd = record['lbd_fvp_b1l_clinical_symptoms_and_exam_complete']
        if form_match_lbd in ['0', '']:
            return False
    elif options.ftld and options.ivp:
        event_name = 'initial'
        form_match_ftld = record['ftld_present']
        if form_match_ftld in ['0', '']:
            return False
    elif options.ftld and options.fvp:
        event_name = 'follow'
        form_match_ftld = record['fu_ftld_present']
        if form_match_ftld in ['0', '']:
            return False
    elif options.ivp:
        event_name = 'initial'
        try:
            form_match_z1 = record['ivp_z1_complete']
        except KeyError:
            form_match_z1 = ''
            record['ivp_z1_complete'] = ''
        form_match_z1x = record['ivp_z1x_complete']
        if form_match_z1 in ['0', ''] and form_match_z1x in ['0', '']:
            return False
    elif options.fvp:
        event_name = 'follow'
        try:
            form_match_z1 = record['fvp_z1_complete']
        except KeyError:
            form_match_z1 = ''
            record['fvp_z1_complete'] = ''
        form_match_z1x = record['fvp_z1x_complete']
        if form_match_z1 in ['0', ''] and form_match_z1x in ['0', '']:
            return False
    # TODO: add -csf option if/when it is added to the full ADRC project.
    elif options.cv:
        event_name = 'covid'
    elif options.np:
        event_name = 'neuropath'
    elif options.tfp:
        event_name = 'follow'
        try:
            followup_match = record['tvp_z1x_checklist_complete']
            if followup_match in ['', '0']:
                return False
        except KeyError:
            try:
                followup_match = record['tfp_z1x_complete']
                if followup_match in ['', '0']:
                    return False
            except KeyError:
                try:
                    followup_match = record['tele_z1x_complete']
                    if followup_match in ['', '0']:
                        return False
                except KeyError:
                    print("Could not find a REDCap field for TFP Z1X form.", file=err)
                    return False
    elif options.tfp3:
        event_name = 'tele'
    elif options.m:
        event_name = 'milestone'

    redcap_event = record['redcap_event_name']
    event_match = event_name in redcap_event
    return event_match


def check_single_select(packet: uds3_packet.Packet):
    """ Checks the values of sets of interdependent questions

    There are some sets of questions which should function like an HTML radio
    button group in that only one of them should be selected. However, because
    of the manner in which they were implemented in REDCap, the values need to
    be double-checked to ensure at most one in a given set has the real answer.
    """
    warnings = list()

    # TODO: get these checks actually working.
    # D1 4
    fields_4 = ('AMNDEM', 'PCA', 'PPASYN', 'FTDSYN', 'LBDSYN', 'NAMNDEM')
    if not exclusive(packet, fields_4):
        warnings.append('For Form D1, Question 4, there is unexpectedly more '
                        'than one syndrome indicated as "Present".')

    # D1 5
    fields_5 = ('MCIAMEM', 'MCIAPLUS', 'MCINON1', 'MCINON2', 'IMPNOMCI')
    if not exclusive(packet, fields_5):
        warnings.append('For Form D1, Question 5, there is unexpectedly more '
                        'than one syndrome indicated as "Present".')

    # D1 11-39
    fields_11_39 = ('ALZDISIF', 'LBDIF', 'MSAIF', 'PSPIF', 'CORTIF',
                    'FTLDMOIF', 'FTLDNOIF', 'FTLDSUBX', 'CVDIF', 'ESSTREIF',
                    'DOWNSIF', 'HUNTIF', 'PRIONIF', 'BRNINJIF', 'HYCEPHIF',
                    'EPILEPIF', 'NEOPIF', 'HIVIF', 'OTHCOGIF', 'DEPIF',
                    'BIPOLDIF', 'SCHIZOIF', 'ANXIETIF', 'DELIRIF', 'PTSDDXIF',
                    'OTHPSYIF', 'ALCDEMIF', 'IMPSUBIF', 'DYSILLIF', 'MEDSIF',
                    'COGOTHIF', 'COGOTH2F', 'COGOTH3F')
    if not exclusive(packet, fields_11_39):
        warnings.append('For Form D1, Questions 11-39, there is unexpectedly '
                        'more than one Primary cause selected.')

    return warnings


def empty(field):
    """ Helper function that returns True if a field's value is empty """
    return field.value.strip() == ""


def exclusive(packet, fields, value_to_check=1):
    """ Returns True iff, for a set of fields, only one of field is set. """
    values = [packet[f].value for f in fields]
    true_values = [v for v in values if v == value_to_check]
    return len(true_values) <= 1


def set_blanks_to_zero(packet):
    """ Sets specific fields to zero if they meet certain criteria """
    def set_to_zero_if_blank(*field_names):
        for field_name in field_names:
            field = packet[field_name]
            if empty(field):
                field.value = 0

    # B6 G1.
    try:
        if packet['GDS'] in range(0, 15):
            set_to_zero_if_blank('NOGDS')
    except KeyError:
        pass

    # B8 2.
    try:
        if packet['PARKSIGN'] == 1:
            set_to_zero_if_blank(
                'RESTTRL', 'RESTTRR', 'SLOWINGL', 'SLOWINGR', 'RIGIDL', 'RIGIDR',
                'BRADY', 'PARKGAIT', 'POSTINST')
    except KeyError:
        pass

    # B8 3.
    try:
        if packet['CVDSIGNS'] == 1:
            set_to_zero_if_blank('CORTDEF', 'SIVDFIND', 'CVDMOTL', 'CVDMOTR',
                                'CORTVISL', 'CORTVISR', 'SOMATL', 'SOMATR')
    except KeyError:
        pass

    # B8 5.
    try:
        if packet['PSPCBS'] == 1:
            set_to_zero_if_blank(
                'PSPCBS', 'EYEPSP', 'DYSPSP', 'AXIALPSP', 'GAITPSP', 'APRAXSP',
                'APRAXL', 'APRAXR', 'CORTSENL', 'CORTSENR', 'ATAXL', 'ATAXR',
                'ALIENLML', 'ALIENLMR', 'DYSTONL', 'DYSTONR', 'MYOCLLT',
                'MYOCLRT')
    except KeyError:
        pass

    # D1 4.
    try:
        if packet['DEMENTED'] == 1:
            set_to_zero_if_blank(
                    'AMNDEM', 'PCA', 'PPASYN', 'FTDSYN', 'LBDSYN', 'NAMNDEM')
    except KeyError:
        pass

    # D1 5.
    try:
        if packet['DEMENTED'] == 0:
            set_to_zero_if_blank(
                    'MCIAMEM', 'MCIAPLUS', 'MCINON1', 'MCINON2', 'IMPNOMCI')
    except KeyError:
        pass

    # D1 11-39.
    try:
        set_to_zero_if_blank(
            'ALZDIS', 'LBDIS', 'MSA', 'PSP', 'CORT', 'FTLDMO', 'FTLDNOS', 'CVD',
            'ESSTREM', 'DOWNS', 'HUNT', 'PRION', 'BRNINJ', 'HYCEPH', 'EPILEP',
            'NEOP', 'HIV', 'OTHCOG', 'DEP', 'BIPOLDX', 'SCHIZOP', 'ANXIET',
            'DELIR', 'PTSDDX', 'OTHPSY', 'ALCDEM', 'IMPSUB', 'DYSILL', 'MEDS',
            'COGOTH', 'COGOTH2', 'COGOTH3')
    except KeyError:
        pass

    # D2 11.
    try:
        if packet['ARTH'] == 1:
            set_to_zero_if_blank('ARTUPEX', 'ARTLOEX', 'ARTSPIN', 'ARTUNKN')
    except KeyError:
        pass


def convert(fp, options, out=sys.stdout, err=sys.stderr):
    """Converts data in REDCap's CSV format to NACC's fixed-width format."""
    reader = csv.DictReader(fp)
    for record in reader:
        # Right now the csf form is a single non-longitudinal form in a
        # separate REDCap project with no redcap_event_name.
        if not options.csf:
            event_match = check_redcap_event(options, record)
            if not event_match:
                continue

        print("[START] ptid : " + str(record['ptid']), file=err)
        try:
            if options.lbd and options.ivp:
                packet = lbd_ivp_builder.build_lbd_ivp_form(record)
            elif options.lbd and options.fvp:
                packet = lbd_fvp_builder.build_lbd_fvp_form(record)
            elif options.lbdsv and options.ivp:
                packet = lbd_short_ivp_builder.build_lbd_short_ivp_form(record)
            elif options.lbdsv and options.fvp:
                packet = lbd_short_fvp_builder.build_lbd_short_fvp_form(record)
            elif options.ftld and options.ivp:
                packet = ftld_ivp_builder.build_ftld_ivp_form(record)
            elif options.ftld and options.fvp:
                packet = ftld_fvp_builder.build_ftld_fvp_form(record)
            elif options.csf:
                packet = csf_builder.build_csf_form(record)
            elif options.cv:
                packet = cv_builder.build_cv_form(record)
            elif options.ivp:
                packet = ivp_builder.build_uds3_ivp_form(record)
            elif options.np:
                packet = np_builder.build_uds3_np_form(record)
            elif options.fvp:
                packet = fvp_builder.build_uds3_fvp_form(record)
            elif options.tfp:
                packet = tfp_new_builder.build_uds3_tfp_new_form(record)
            elif options.tfp3:
                packet = tfp_builder.build_uds3_tfp_form(record)
            elif options.m:
                packet = m_builder.build_uds3_m_form(record)

        except Exception:
            if 'ptid' in record:
                print("[SKIP] Error for ptid : " + str(record['ptid']),
                      file=err)
            traceback.print_exc()
            continue

        if not (options.np or options.m or options.lbd or options.lbdsv or
                options.ftld or options.csf or options.cv):
            set_blanks_to_zero(packet)

        if options.m or options.tfp:
            blanks_uds3.set_zeros_to_blanks(packet)

        warnings = []
        try:
            warnings += check_blanks(packet, options)
        except KeyError:
            print("[SKIP] Error for ptid : " + str(record['ptid']), file=err)
            traceback.print_exc()
            continue

        try:
            warnings += check_characters(packet)
        except KeyError:
            print("[SKIP] Error for ptid : " + str(record['ptid']), file=err)
            traceback.print_exc()
            continue

        if warnings:
            print("[SKIP] Error for ptid : " + str(record['ptid']),
                  file=err)
            warn = "\n".join(map(str, warnings))
            warn = warn.replace("\\", "")
            print(warn, file=err)
            continue

        if not options.np and not options.m and not options.lbd and not \
           options.lbdsv and not options.ftld and not options.csf and not \
           options.cv:
            warnings += check_single_select(packet)

        for form in packet:

            try:
                print(form, file=out)
            except AssertionError:
                print("[SKIP] Error for ptid : " + str(record['ptid']),
                      file=err)
                traceback.print_exc()
                continue


filters_names = {
    'cleanPtid': 'clean_ptid',
    'replaceDrugId': 'replace_drug_id',
    'fixHeaders': 'fix_headers',
    'fillDefault': 'fill_default',
    'updateField': 'update_field',
    'removePtid': 'remove_ptid',
    'removeDateRecord': 'eliminate_empty_date',
    'getPtid': 'extract_ptid'}


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        description='Process redcap form output to nacculator.')

    option_group = parser.add_mutually_exclusive_group()
    option_group.add_argument(
        '-fvp', action='store_true', dest='fvp',
        help='Set this flag to process as fvp data')
    option_group.add_argument(
        '-ivp', action='store_true', dest='ivp',
        help='Set this flag to process as ivp data')
    option_group.add_argument(
        '-tfp', action='store_true', dest='tfp',
        help='Set this flag to process as tfp version 3.2 data')
    option_group.add_argument(
        '-tfp3', action='store_true', dest='tfp3',
        help='Set this flag to process as tfp version 3.0 (pre-June 2020) data')
    option_group.add_argument(
        '-np', action='store_true', dest='np',
        help='Set this flag to process as np data')
    option_group.add_argument(
        '-m', action='store_true', dest='m',
        help='Set this flag to process as m data')
    option_group.add_argument(
        '-f', '--filter', action='store', dest='filter',
        choices=list(filters_names.keys()),
        help='Set this flag to process the filter')

    parser.add_argument(
        '-lbd', action='store_true', dest='lbd',
        help='Set this flag to process as Lewy Body Dementia data')
    parser.add_argument(
        '-lbdsv', action='store_true', dest='lbdsv',
        help='Set this flag to process as Lewy Body Dementia short version data')
    parser.add_argument(
        '-ftld', action='store_true', dest='ftld',
        help='Set this flag to process as Frontotemporal Lobar'
        ' Degeneration data')
    parser.add_argument(
        '-csf', action='store_true', dest='csf',
        help='Set this flag to process as Cerebrospinal Fluid data')
    parser.add_argument(
        '-cv', action='store_true', dest='cv',
        help='Set this flag to process as COVID-19 data')
    parser.add_argument(
        '-file', action='store', dest='file',
        help='Path of the csv file to be processed.')
    parser.add_argument(
        '-meta', action='store', dest='filter_meta',
        help='Input file for the filter metadata (in case -filter is used)')
    parser.add_argument(
        '-ptid', action='store', dest='ptid',
        help='Ptid for which you need the records')
    parser.add_argument(
        '-vnum', action='store', dest='vnum',
        help='Ptid for which you need the records')
    parser.add_argument(
        '-vtype', action='store', dest='vtype',
        help='Ptid for which you need the records')

    options = parser.parse_args(args)
    # Defaults to processing of ivp.
    # TODO this can be changed in future to process fvp by default.
    if not (options.ivp or options.fvp or options.tfp or options.tfp3 or
            options.np or options.m or options.csf or options.cv or
            options.filter):
        options.ivp = True

    return options


def main():
    """
    Reads a REDCap exported CSV, data file, then prints it out in NACC's format
    """
    options = parse_args()

    fp = sys.stdin if options.file is None else open(options.file, 'r')

    # Place holder for future. May need to output to a specific file in future.
    output = sys.stdout

    if options.filter:
        if options.filter == "getPtid":
            filters.filter_extract_ptid(
                fp, options.ptid, options.vnum, options.vtype, output)
        else:
            filter_method = 'filter_' + filters_names[options.filter]
            filter_func = getattr(filters, filter_method)
            filter_func(fp, options.filter_meta, output)
    else:
        convert(fp, options)


if __name__ == '__main__':
    main()
