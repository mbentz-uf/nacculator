###############################################################################
# Copyright 2015-2020 University of Florida. All rights reserved.
# This file is part of UF CTS-IT's NACCulator project.
# Use of this source code is governed by the license found in the LICENSE file.
###############################################################################

import sys

from nacc.ftld.ivp import forms as ftld_ivp_forms
from nacc.uds3 import packet as ftld_ivp_packet


def build_ftld_ivp_form(record: dict, err=sys.stderr):
    ''' Converts REDCap CSV data into a packet (list of IVP Form objects) '''
    packet = ftld_ivp_packet.Packet()

    # Set up the forms..........

    # This form cannot precede March 1, 2015.
    if not (int(record['visityr']) > 2015) or \
        (int(record['visityr']) == 2015 and int(record['visitmo']) > 3) or \
            (int(record['visityr']) == 2015 and int(record['visitmo']) == 3
                and int(record['visitday']) >= 1):
        raise ValueError('Form date cannot precede March 1, 2015.')

    add_z1x(record, packet)
    # Forms B3F, B9F, C1F, C2F, C3F, E2F, and E3F are REQUIRED.
    # Forms A3A, C4F, C5F, and C6F are OPTIONAL and must be specifically
    # marked as present for nacculator to process them
    if record['ivp_z1x_complete'] in ['1', '2']:
        try:
            if record['ftda3afs'] == '1':
                add_a3a(record, packet)
        except KeyError:
            pass
        add_b3f(record, packet)
        add_b9f(record, packet)
        add_c1f(record, packet)
        add_c2f(record, packet)
        add_c3f(record, packet)
        try:
            if record['ftdc4fs'] == '1':
                add_c4f(record, packet)
        except KeyError:
            pass
        try:
            if record['ftdc5fs'] == '1':
                add_c5f(record, packet)
        except KeyError:
            pass
        try:
            if record['ftdc6fs'] == '1':
                add_c6f(record, packet)
        except KeyError:
            pass
    else:
        print("ptid " + str(record['ptid']) +
              ": No Z1X form found.", file=err)
    add_e2f(record, packet)
    add_e3f(record, packet)
    update_header(record, packet)

    return packet


def add_z1x(record, packet):
    Z1X = ftld_ivp_forms.FormZ1X()
    Z1X.LANGA1   = record['langa1']
    Z1X.LANGA2   = record['langa2']
    Z1X.A2SUB    = record['a2sub']
    Z1X.A2NOT    = record['a2not']
    Z1X.LANGA3   = record['langa3']
    Z1X.A3SUB    = record['a3sub']
    Z1X.A3NOT    = record['a3not']
    Z1X.LANGA4   = record['langa4']
    Z1X.A4SUB    = record['a4sub']
    Z1X.A4NOT    = record['a4not']
    Z1X.LANGA5   = record['langa5']
    Z1X.LANGB1   = record['langb1']
    Z1X.B1SUB    = record['b1sub']
    Z1X.B1NOT    = record['b1not']
    Z1X.LANGB4   = record['langb4']
    Z1X.LANGB5   = record['langb5']
    Z1X.B5SUB    = record['b5sub']
    Z1X.B5NOT    = record['b5not']
    Z1X.LANGB6   = record['langb6']
    Z1X.B6SUB    = record['b6sub']
    Z1X.B6NOT    = record['b6not']
    Z1X.LANGB7   = record['langb7']
    Z1X.B7SUB    = record['b7sub']
    Z1X.B7NOT    = record['b7not']
    Z1X.LANGB8   = record['langb8']
    Z1X.LANGB9   = record['langb9']
    Z1X.LANGC2   = record['langc2']
    Z1X.LANGD1   = record['langd1']
    Z1X.LANGD2   = record['langd2']
    Z1X.LANGA3A  = record['langa3a']
    Z1X.FTDA3AFS = record['ftda3afs']
    Z1X.FTDA3AFR = record['ftda3afr']
    Z1X.LANGB3F  = record['langb3f']
    Z1X.LANGB9F  = record['langb9f']
    Z1X.LANGC1F  = record['langc1f']
    Z1X.LANGC2F  = record['langc2f']
    Z1X.LANGC3F  = record['langc3f']
    Z1X.LANGC4F  = record['langc4f']
    Z1X.FTDC4FS  = record['ftdc4fs']
    Z1X.FTDC4FR  = record['ftdc4fr']
    Z1X.LANGC5F  = record['langc5f']
    Z1X.FTDC5FS  = record['ftdc5fs']
    Z1X.FTDC5FR  = record['ftdc5fr']
    Z1X.LANGC6F  = record['langc6f']
    Z1X.FTDC6FS  = record['ftdc6fs']
    Z1X.FTDC6FR  = record['ftdc6fr']
    Z1X.LANGE2F  = record['lange2f']
    Z1X.LANGE3F  = record['lange3f']
    Z1X.LANGCLS  = record['langcls']
    Z1X.CLSSUB   = record['clssub']
    # for REDCap projects that don't have the LBD questions added to their Z1X,
    # we just see if there's info in the B2L and B6L forms and fill in
    # accordingly.
    try:
        Z1X.B2LSUB  = record['b2lsub']
        Z1X.B2LNOT  = record['b2lnot']
        Z1X.B6LSUB  = record['b6lsub']
        Z1X.B6LNOT  = record['b6lnot']
    except KeyError:
        try:
            if record['lbudspch'] in ['0', '1']:
                Z1X.B2LSUB = '1'
                Z1X.B2LNOT = ''
            if record['lbspcgim'] in ['0', '1']:
                Z1X.B6LSUB = '1'
                Z1X.B6LNOT = ''
        # And leave the LBD fields blank if the project does not contain the
        # LBD module
        except KeyError:
            Z1X.B2LSUB = ''
            Z1X.B2LNOT = ''
            Z1X.B6LSUB = ''
            Z1X.B6LNOT = ''
    packet.insert(0, Z1X)


def add_a3a(record, packet):
    A3a = ftld_ivp_forms.FormA3a()
    A3a.FTDRELCO = record['ftdrelco']
    A3a.FTDSIBBY = record['ftdsibby']
    A3a.FTDChDBY = record['ftdchdby']
    A3a.FTDSTORE = record['ftdstore']
    A3a.FTDSLEAR = record['ftdslear']
    A3a.FTDCOMME = record['ftdcomme']
    packet.append(A3a)


def add_b3f(record, packet):
    B3F = ftld_ivp_forms.FormB3F()
    B3F.FTDLTFAS = record['ftdltfas']
    B3F.FTDLIMB  = record['ftdlimb']
    B3F.FTDBULB  = record['ftdbulb']
    B3F.FTDGSEV  = record['ftdgsev']
    B3F.FTDGSEVX = record['ftdgsevx']
    B3F.FTDGTYP  = record['ftdgtyp']
    B3F.FTDGTYPG = record['ftdgtypg']
    B3F.FTDGTYPX = record['ftdgtypx']
    packet.append(B3F)


def add_b9f(record, packet):
    B9F = ftld_ivp_forms.FormB9F()
    B9F.FTDPPASL = record['ftdppasl']
    B9F.FTDPPAPO = record['ftdppapo']
    B9F.FTDPPAIW = record['ftdppaiw']
    B9F.FTDPPASW = record['ftdppasw']
    B9F.FTDPPAPK = record['ftdppapk']
    B9F.FTDPPAGS = record['ftdppags']
    B9F.FTDPPAEh = record['ftdppaeh']
    B9F.FTDPPACS = record['ftdppacs']
    B9F.FTDPPASS = record['ftdppass']
    B9F.FTDPPASR = record['ftdppasr']
    B9F.FTDPPASD = record['ftdppasd']
    B9F.FTDCPPA  = record['ftdcppa']
    B9F.FTDCPPAS = record['ftdcppas']
    B9F.FTDBVCLN = record['ftdbvcln']
    B9F.FTDBVDIS = record['ftdbvdis']
    B9F.FTDBVAPA = record['ftdbvapa']
    B9F.FTDBVLOS = record['ftdbvlos']
    B9F.FTDBVRIT = record['ftdbvrit']
    B9F.FTDBVhYP = record['ftdbvhyp']
    B9F.FTDBVNEU = record['ftdbvneu']
    B9F.FTDBVIDL = record['ftdbvidl']
    B9F.FTDBVFT  = record['ftdbvft']
    B9F.FTDEMGPV = record['ftdemgpv']
    B9F.FTDEMGPY = record['ftdemgpy']
    B9F.FTDEMGMN = record['ftdemgmn']
    B9F.FTDPABVF = record['ftdpabvf']
    packet.append(B9F)


def add_c1f(record, packet):
    C1F = ftld_ivp_forms.FormC1F()
    C1F.FTDWORRC = record['ftdworrc']
    C1F.FTDWORRS = record['ftdworrs']
    C1F.FTDWORRR = record['ftdworrr']
    C1F.FTDWORIC = record['ftdworic']
    C1F.FTDWORIS = record['ftdworis']
    C1F.FTDWORIR = record['ftdworir']
    C1F.FTDWORIP = record['ftdworip']
    C1F.FTDSEMMT = record['ftdsemmt']
    C1F.FTDSEMAA = record['ftdsemaa']
    C1F.FTDSEMTA = record['ftdsemta']
    C1F.FTDSEMSU = record['ftdsemsu']
    C1F.FTDANASW = record['ftdanasw']
    C1F.FTDANAOW = record['ftdanaow']
    C1F.FTDANATS = record['ftdanats']
    C1F.FTDSENAS = record['ftdsenas']
    C1F.FTDSENOS = record['ftdsenos']
    C1F.FTDSENSR = record['ftdsensr']
    C1F.FTDSENPR = record['ftdsenpr']
    C1F.FTDNOUNC = record['ftdnounc']
    C1F.FTDVERBC = record['ftdverbc']
    C1F.FTDRATIO = record['ftdratio']
    C1F.FTDREAAS = record['ftdreaas']
    C1F.FTDREAOS = record['ftdreaos']
    C1F.FTDREASR = record['ftdreasr']
    C1F.FTDREAPR = record['ftdreapr']
    packet.append(C1F)


def add_c2f(record, packet):
    C2F = ftld_ivp_forms.FormC2F()
    C2F.FTDCPC2F = record['ftdcpc2f']
    C2F.FTDhAIRD = record['ftdhaird']
    C2F.FTDSPIT  = record['ftdspit']
    C2F.FTDNOSE  = record['ftdnose']
    C2F.FTDCOAGE = record['ftdcoage']
    C2F.FTDCRY   = record['ftdcry']
    C2F.FTDCUT   = record['ftdcut']
    C2F.FTDYTRIP = record['ftdytrip']
    C2F.FTDEATP  = record['ftdeatp']
    C2F.FTDTELLA = record['ftdtella']
    C2F.FTDOPIN  = record['ftdopin']
    C2F.FTDLAUGh = record['ftdlaugh']
    C2F.FTDShIRT = record['ftdshirt']
    C2F.FTDKEEPM = record['ftdkeepm']
    C2F.FTDPICKN = record['ftdpickn']
    C2F.FTDOVER  = record['ftdover']
    C2F.FTDEATR  = record['ftdeatr']
    C2F.FTDhAIRL = record['ftdhairl']
    C2F.FTDShIRW = record['ftdshirw']
    C2F.FTDMOVE  = record['ftdmove']
    C2F.FTDhUGS  = record['ftdhugs']
    C2F.FTDLOUD  = record['ftdloud']
    C2F.FTDLOST  = record['ftdlost']
    C2F.FTDSNTOT = record['ftdsntot']
    C2F.FTDSNTBS = record['ftdsntbs']
    C2F.FTDSNTOS = record['ftdsntos']
    C2F.FTDSNRAT = record['ftdsnrat']
    packet.append(C2F)


def add_c3f(record, packet):
    C3F = ftld_ivp_forms.FormC3F()
    C3F.FTDSELF  = record['ftdself']
    C3F.FTDBADLY = record['ftdbadly']
    C3F.FTDDEPR  = record['ftddepr']
    C3F.FTDEMOTD = record['ftdemotd']
    C3F.FTDLSELF = record['ftdlself']
    C3F.FTDDISR  = record['ftddisr']
    C3F.FTDBELCh = record['ftdbelch']
    C3F.FTDGIGG  = record['ftdgigg']
    C3F.FTDPRIV  = record['ftdpriv']
    C3F.FTDNEGAT = record['ftdnegat']
    C3F.FTDECOMM = record['ftdecomm']
    C3F.FTDINAPJ = record['ftdinapj']
    C3F.FTDFAILA = record['ftdfaila']
    C3F.FTDRESIS = record['ftdresis']
    C3F.FTDINTER = record['ftdinter']
    C3F.FTDVERBA = record['ftdverba']
    C3F.FTDPhYSI = record['ftdphysi']
    C3F.FTDTOPIC = record['ftdtopic']
    C3F.FTDPROTO = record['ftdproto']
    C3F.FTDPREO  = record['ftdpreo']
    C3F.FTDFINI  = record['ftdfini']
    C3F.FTDACTED = record['ftdacted']
    C3F.FTDABS   = record['ftdabs']
    C3F.FTDFEEDB = record['ftdfeedb']
    C3F.FTDFRUST = record['ftdfrust']
    C3F.FTDANXI  = record['ftdanxi']
    C3F.FTDNERVO = record['ftdnervo']
    C3F.FTDNDIAG = record['ftdndiag']
    C3F.FTDSTIMB = record['ftdstimb']
    C3F.FTDSTIME = record['ftdstime']
    C3F.FTDOBJEC = record['ftdobjec']
    C3F.FTDCIRCU = record['ftdcircu']
    C3F.FTDPERSE = record['ftdperse']
    C3F.FTDREPEA = record['ftdrepea']
    C3F.FTDANECD = record['ftdanecd']
    C3F.FTDDINIT = record['ftddinit']
    C3F.FTDDELAY = record['ftddelay']
    C3F.FTDADDVE = record['ftdaddve']
    C3F.FTDFLUCT = record['ftdfluct']
    C3F.FTDLOSTT = record['ftdlostt']
    C3F.FTDREPRU = record['ftdrepru']
    C3F.FTDTRAIN = record['ftdtrain']
    C3F.FTDDISCL = record['ftddiscl']
    C3F.FTDSPONT = record['ftdspont']
    C3F.FTDSPONR = record['ftdsponr']
    C3F.FTDSTOOD = record['ftdstood']
    C3F.FTDTOUCh = record['ftdtouch']
    C3F.FTDDSOCI = record['ftddsoci']
    C3F.FTDEXAGG = record['ftdexagg']
    C3F.FTDSBTOT = record['ftdsbtot']
    C3F.FTDSBCTO = record['ftdsbcto']
    C3F.FTDLENGT = record['ftdlengt']
    packet.append(C3F)


def add_c4f(record, packet):
    C4F = ftld_ivp_forms.FormC4F()
    C4F.FTDCPC4F = record['ftdcpc4f']
    C4F.FTDWORKU = record['ftdworku']
    C4F.FTDMIST  = record['ftdmist']
    C4F.FTDCRIT  = record['ftdcrit']
    C4F.FTDWORR  = record['ftdworr']
    C4F.FTDBAD   = record['ftdbad']
    C4F.FTDPOOR  = record['ftdpoor']
    C4F.FTDFFEAR = record['ftdffear']
    C4F.FTDBIST  = record['ftdbist']
    packet.append(C4F)


def add_c5f(record, packet):
    C5F = ftld_ivp_forms.FormC5F()
    C5F.FTDCPC5F = record['ftdcpc5f']
    C5F.FTDINSEX = record['ftdinsex']
    C5F.FTDINFMO = record['ftdinfmo']
    C5F.FTDINFYR = record['ftdinfyr']
    C5F.FTDINFRE = record['ftdinfre']
    C5F.FTDFEEL  = record['ftdfeel']
    C5F.FTDDIFF  = record['ftddiff']
    C5F.FTDSORR  = record['ftdsorr']
    C5F.FTDSIDE  = record['ftdside']
    C5F.FTDADVAN = record['ftdadvan']
    C5F.FTDIMAG  = record['ftdimag']
    C5F.FTDMISF  = record['ftdmisf']
    C5F.FTDWASTE = record['ftdwaste']
    C5F.FTDPITY  = record['ftdpity']
    C5F.FTDQTOUC = record['ftdqtouc']
    C5F.FTDSIDES = record['ftdsides']
    C5F.FTDSOFTh = record['ftdsofth']
    C5F.FTDUPSET = record['ftdupset']
    C5F.FTDCRITI = record['ftdcriti']
    C5F.FTDIRIEC = record['ftdiriec']
    C5F.FTDIRIPT = record['ftdiript']
    packet.append(C5F)


def add_c6f(record, packet):
    C6F = ftld_ivp_forms.FormC6F()
    C6F.FTDCPC6F = record['ftdcpc6f']
    C6F.FTDALTER = record['ftdalter']
    C6F.FTDEMOT  = record['ftdemot']
    C6F.FTDACROS = record['ftdacros']
    C6F.FTDCONV  = record['ftdconv']
    C6F.FTDINTUI = record['ftdintui']
    C6F.FTDJOKE  = record['ftdjoke']
    C6F.FTDIMAGP = record['ftdimagp']
    C6F.FTDINAPP = record['ftdinapp']
    C6F.FTDChBEh = record['ftdchbeh']
    C6F.FTDADBEh = record['ftdadbeh']
    C6F.FTDLYING = record['ftdlying']
    C6F.FTDGOODF = record['ftdgoodf']
    C6F.FTDREGUL = record['ftdregul']
    C6F.FTDSMSCR = record['ftdsmscr']
    C6F.FTDSPSCR = record['ftdspscr']
    C6F.FTDRSMST = record['ftdrsmst']
    packet.append(C6F)


def add_e2f(record, packet):
    E2F = ftld_ivp_forms.FormE2F()
    E2F.FTDSMRI  = record['ftdsmri']
    E2F.FTDSMMO  = record['ftdsmmo']
    E2F.FTDSMDY  = record['ftdsmdy']
    E2F.FTDSMYR  = record['ftdsmyr']
    E2F.FTDSMDIC = record['ftdsmdic']
    E2F.FTDSMDIS = record['ftdsmdis']
    E2F.FTDSMADN = record['ftdsmadn']
    E2F.FTDSMADV = record['ftdsmadv']
    E2F.FTDSMMAN = record['ftdsmman']
    E2F.FTDSMMAO = record['ftdsmmao']
    E2F.FTDSMMAM = record['ftdsmmam']
    E2F.FTDSMFS  = record['ftdsmfs']
    E2F.FTDSMFSO = record['ftdsmfso']
    E2F.FTDSMQU  = record['ftdsmqu']
    E2F.FTDFDGPT = record['ftdfdgpt']
    E2F.FTDFPMO  = record['ftdfpmo']
    E2F.FTDFPDY  = record['ftdfpdy']
    E2F.FTDFPYR  = record['ftdfpyr']
    E2F.FTDFDDIC = record['ftdfddic']
    E2F.FTDFDDID = record['ftdfddid']
    E2F.FTDFDADN = record['ftdfdadn']
    E2F.FTDFDADV = record['ftdfdadv']
    E2F.FTDFDMAN = record['ftdfdman']
    E2F.FTDFDMAO = record['ftdfdmao']
    E2F.FTDFDMAM = record['ftdfdmam']
    E2F.FTDFDQU  = record['ftdfdqu']
    E2F.FTDAMYPT = record['ftdamypt']
    E2F.FTDAMMO  = record['ftdammo']
    E2F.FTDAMDY  = record['ftdamdy']
    E2F.FTDAMYR  = record['ftdamyr']
    E2F.FTDAMDIC = record['ftdamdic']
    E2F.FTDAMDID = record['ftdamdid']
    E2F.FTDAMLIG = record['ftdamlig']
    E2F.FTDAMLIO = record['ftdamlio']
    E2F.FTDAMADN = record['ftdamadn']
    E2F.FTDAMADV = record['ftdamadv']
    E2F.FTDAMMAN = record['ftdamman']
    E2F.FTDAMMAO = record['ftdammao']
    E2F.FTDAMMAM = record['ftdammam']
    E2F.FTDAMQU  = record['ftdamqu']
    E2F.FTDOThER = record['ftdother']
    E2F.FTDOTDOP = record['ftdotdop']
    E2F.FTDOTSER = record['ftdotser']
    E2F.FTDOTChO = record['ftdotcho']
    E2F.FTDOTANO = record['ftdotano']
    E2F.FTDOTANS = record['ftdotans']
    packet.append(E2F)


def add_e3f(record, packet):
    E3F = ftld_ivp_forms.FormE3F()
    E3F.FTDIDIAG = record['ftdidiag']
    E3F.FTDSMRIO = record['ftdsmrio']
    E3F.FTDMRIFA = record['ftdmrifa']
    E3F.FTDMRIRF = record['ftdmrirf']
    E3F.FTDMRILF = record['ftdmrilf']
    E3F.FTDMRIRT = record['ftdmrirt']
    E3F.FTDMRILT = record['ftdmrilt']
    E3F.FTDMRIRM = record['ftdmrirm']
    E3F.FTDMRILM = record['ftdmrilm']
    E3F.FTDMRIRP = record['ftdmrirp']
    E3F.FTDMRILP = record['ftdmrilp']
    E3F.FTDMRIRB = record['ftdmrirb']
    E3F.FTDMRILB = record['ftdmrilb']
    E3F.FTDMRIOB = record['ftdmriob']
    E3F.FTDMRIOS = record['ftdmrios']
    E3F.FTDFDGPE = record['ftdfdgpe']
    E3F.FTDFDGFh = record['ftdfdgfh']
    E3F.FTDFDGRF = record['ftdfdgrf']
    E3F.FTDFDGLF = record['ftdfdglf']
    E3F.FTDFDGRT = record['ftdfdgrt']
    E3F.FTDFDGLT = record['ftdfdglt']
    E3F.FTDFDGRM = record['ftdfdgrm']
    E3F.FTDFDGLM = record['ftdfdglm']
    E3F.FTDFDGRP = record['ftdfdgrp']
    E3F.FTDFDGLP = record['ftdfdglp']
    E3F.FTDFDGRB = record['ftdfdgrb']
    E3F.FTDFDGLB = record['ftdfdglb']
    E3F.FTDFDGOA = record['ftdfdgoa']
    E3F.FTDFDGOS = record['ftdfdgos']
    E3F.FTDAMYP  = record['ftdamyp']
    E3F.FTDAMYVI = record['ftdamyvi']
    E3F.FTDAMYRF = record['ftdamyrf']
    E3F.FTDAMYLF = record['ftdamylf']
    E3F.FTDAMYRT = record['ftdamyrt']
    E3F.FTDAMYLT = record['ftdamylt']
    E3F.FTDAMYRM = record['ftdamyrm']
    E3F.FTDAMYLM = record['ftdamylm']
    E3F.FTDAMYRP = record['ftdamyrp']
    E3F.FTDAMYLP = record['ftdamylp']
    E3F.FTDAMYRB = record['ftdamyrb']
    E3F.FTDAMYLB = record['ftdamylb']
    E3F.FTDAMYOA = record['ftdamyoa']
    E3F.FTDAMYOS = record['ftdamyos']
    E3F.FTDCBFSP = record['ftdcbfsp']
    E3F.FTDCBFVI = record['ftdcbfvi']
    E3F.FTDCBFRF = record['ftdcbfrf']
    E3F.FTDCBFLF = record['ftdcbflf']
    E3F.FTDCBFRT = record['ftdcbfrt']
    E3F.FTDCBFLT = record['ftdcbflt']
    E3F.FTDCBFRM = record['ftdcbfrm']
    E3F.FTDCBFLM = record['ftdcbflm']
    E3F.FTDCBFRP = record['ftdcbfrp']
    E3F.FTDCBFLP = record['ftdcbflp']
    E3F.FTDCBFRB = record['ftdcbfrb']
    E3F.FTDCBFLB = record['ftdcbflb']
    E3F.FTDCBFOA = record['ftdcbfoa']
    E3F.FTDCBFOS = record['ftdcbfos']
    E3F.FTDOTHI  = record['ftdothi']
    E3F.FTDOTHIS = record['ftdothis']
    packet.append(E3F)


def update_header(record, packet):
    for header in packet:
        header.PACKET = "IF"
        header.FORMID = header.form_name
        if header.FORMID == "Z1X":
            header.PACKET = "I"
        header.FORMVER = 3
        header.ADCID = record['adcid']
        header.PTID = record['ptid']
        header.VISITMO = record['visitmo']
        header.VISITDAY = record['visitday']
        header.VISITYR = record['visityr']
        header.VISITNUM = record['visitnum']
        header.INITIALS = record['initials']
