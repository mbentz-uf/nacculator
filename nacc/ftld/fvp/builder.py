###############################################################################
# Copyright 2015-2020 University of Florida. All rights reserved.
# This file is part of UF CTS-IT's NACCulator project.
# Use of this source code is governed by the license found in the LICENSE file.
###############################################################################

import sys

from nacc.ftld.fvp import forms as ftld_fvp_forms
from nacc.uds3 import packet as ftld_fvp_packet


def build_ftld_fvp_form(record: dict, err=sys.stderr):
    ''' Converts REDCap CSV data into a packet (list of FVP Form objects) '''
    packet = ftld_fvp_packet.Packet()

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
    if record['fvp_z1x_complete'] in ['1', '2']:
        try:
            if record['fu_ftda3afs'] == '1':
                add_a3a(record, packet)
        except KeyError:
            pass
        add_b3f(record, packet)
        add_b9f(record, packet)
        add_c1f(record, packet)
        add_c2f(record, packet)
        add_c3f(record, packet)
        try:
            if record['fu_ftdc4fs'] == '1':
                add_c4f(record, packet)
        except KeyError:
            pass
        try:
            if record['fu_ftdc5fs'] == '1':
                add_c5f(record, packet)
        except KeyError:
            pass
        try:
            if record['fu_ftdc6fs'] == '1':
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
    Z1X = ftld_fvp_forms.FormZ1X()
    Z1X.LANGA1   = record['fu_langa1']
    Z1X.LANGA2   = record['fu_langa2']
    Z1X.A2SUB    = record['fu_a2sub']
    Z1X.A2NOT    = record['fu_a2not']
    Z1X.LANGA3   = record['fu_langa3']
    Z1X.A3SUB    = record['fu_a3sub']
    Z1X.A3NOT    = record['fu_a3not']
    Z1X.LANGA4   = record['fu_langa4']
    Z1X.A4SUB    = record['fu_a4sub']
    Z1X.A4NOT    = record['fu_a4not']
    Z1X.LANGB1   = record['fu_langb1']
    Z1X.B1SUB    = record['fu_b1sub']
    Z1X.B1NOT    = record['fu_b1not']
    Z1X.LANGB4   = record['fu_langb4']
    Z1X.LANGB5   = record['fu_langb5']
    Z1X.B5SUB    = record['fu_b5sub']
    Z1X.B5NOT    = record['fu_b5not']
    Z1X.LANGB6   = record['fu_langb6']
    Z1X.B6SUB    = record['fu_b6sub']
    Z1X.B6NOT    = record['fu_b6not']
    Z1X.LANGB7   = record['fu_langb7']
    Z1X.B7SUB    = record['fu_b7sub']
    Z1X.B7NOT    = record['fu_b7not']
    Z1X.LANGB8   = record['fu_langb8']
    Z1X.LANGB9   = record['fu_langb9']
    Z1X.LANGC2   = record['fu_langc2']
    Z1X.LANGD1   = record['fu_langd1']
    Z1X.LANGD2   = record['fu_langd2']
    Z1X.LANGA3A  = record['fu_langa3a']
    Z1X.FTDA3AFS = record['fu_ftda3afs']
    Z1X.FTDA3AFR = record['fu_ftda3afr']
    Z1X.LANGB3F  = record['fu_langb3f']
    Z1X.LANGB9F  = record['fu_langb9f']
    Z1X.LANGC1F  = record['fu_langc1f']
    Z1X.LANGC2F  = record['fu_langc2f']
    Z1X.LANGC3F  = record['fu_langc3f']
    Z1X.LANGC4F  = record['fu_langc4f']
    Z1X.FTDC4FS  = record['fu_ftdc4fs']
    Z1X.FTDC4FR  = record['fu_ftdc4fr']
    Z1X.LANGC5F  = record['fu_langc5f']
    Z1X.FTDC5FS  = record['fu_ftdc5fs']
    Z1X.FTDC5FR  = record['fu_ftdc5fr']
    Z1X.LANGC6F  = record['fu_langc6f']
    Z1X.FTDC6FS  = record['fu_ftdc6fs']
    Z1X.FTDC6FR  = record['fu_ftdc6fr']
    Z1X.LANGE2F  = record['fu_lange2f']
    Z1X.LANGE3F  = record['fu_lange3f']
    Z1X.LANGCLS  = record['fu_langcls']
    Z1X.CLSSUB   = record['fu_clssub']
    # for REDCap projects that don't have the LBD questions added to their Z1X,
    # we just see if there's info in the B2L and B6L forms and fill in
    # accordingly.
    try:
        Z1X.B2LSUB  = record['fu_b2lsub']
        Z1X.B2LNOT  = record['fu_b2lnot']
        Z1X.B6LSUB  = record['fu_b6lsub']
        Z1X.B6LNOT  = record['fu_b6lnot']
    except KeyError:
        try:
            if record['fu_lbudspch'] in ['0', '1']:
                Z1X.B2LSUB = '1'
                Z1X.B2LNOT = ''
            if record['fu_lbspcgim'] in ['0', '1']:
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
    A3a = ftld_fvp_forms.FormA3a()
    A3a.FTDRELCO = record['fu_ftdrelco']
    A3a.FTDSIBBY = record['fu_ftdsibby']
    A3a.FTDChDBY = record['fu_ftdchdby']
    A3a.FTDSTORE = record['fu_ftdstore']
    A3a.FTDSLEAR = record['fu_ftdslear']
    A3a.FTDCOMME = record['fu_ftdcomme']
    packet.append(A3a)


def add_b3f(record, packet):
    B3F = ftld_fvp_forms.FormB3F()
    B3F.FTDLTFAS = record['fu_ftdltfas']
    B3F.FTDLIMB  = record['fu_ftdlimb']
    B3F.FTDBULB  = record['fu_ftdbulb']
    B3F.FTDGSEV  = record['fu_ftdgsev']
    B3F.FTDGSEVX = record['fu_ftdgsevx']
    B3F.FTDGTYP  = record['fu_ftdgtyp']
    B3F.FTDGTYPG = record['fu_ftdgtypg']
    B3F.FTDGTYPX = record['fu_ftdgtypx']
    packet.append(B3F)


def add_b9f(record, packet):
    B9F = ftld_fvp_forms.FormB9F()
    B9F.FTDPPASL = record['fu_ftdppasl']
    B9F.FTDPPAPO = record['fu_ftdppapo']
    B9F.FTDPPAIW = record['fu_ftdppaiw']
    B9F.FTDPPASW = record['fu_ftdppasw']
    B9F.FTDPPAPK = record['fu_ftdppapk']
    B9F.FTDPPAGS = record['fu_ftdppags']
    B9F.FTDPPAEh = record['fu_ftdppaeh']
    B9F.FTDPPACS = record['fu_ftdppacs']
    B9F.FTDPPASS = record['fu_ftdppass']
    B9F.FTDPPASR = record['fu_ftdppasr']
    B9F.FTDPPASD = record['fu_ftdppasd']
    B9F.FTDCPPA  = record['fu_ftdcppa']
    B9F.FTDCPPAS = record['fu_ftdcppas']
    B9F.FTDBVCLN = record['fu_ftdbvcln']
    B9F.FTDBVDIS = record['fu_ftdbvdis']
    B9F.FTDBVAPA = record['fu_ftdbvapa']
    B9F.FTDBVLOS = record['fu_ftdbvlos']
    B9F.FTDBVRIT = record['fu_ftdbvrit']
    B9F.FTDBVhYP = record['fu_ftdbvhyp']
    B9F.FTDBVNEU = record['fu_ftdbvneu']
    B9F.FTDBVIDL = record['fu_ftdbvidl']
    B9F.FTDBVFT  = record['fu_ftdbvft']
    B9F.FTDEMGPV = record['fu_ftdemgpv']
    B9F.FTDEMGPY = record['fu_ftdemgpy']
    B9F.FTDEMGMN = record['fu_ftdemgmn']
    B9F.FTDPABVF = record['fu_ftdpabvf']
    packet.append(B9F)


def add_c1f(record, packet):
    C1F = ftld_fvp_forms.FormC1F()
    C1F.FTDWORRC = record['fu_ftdworrc']
    C1F.FTDWORRS = record['fu_ftdworrs']
    C1F.FTDWORRR = record['fu_ftdworrr']
    C1F.FTDWORIC = record['fu_ftdworic']
    C1F.FTDWORIS = record['fu_ftdworis']
    C1F.FTDWORIR = record['fu_ftdworir']
    C1F.FTDWORIP = record['fu_ftdworip']
    C1F.FTDSEMMT = record['fu_ftdsemmt']
    C1F.FTDSEMAA = record['fu_ftdsemaa']
    C1F.FTDSEMTA = record['fu_ftdsemta']
    C1F.FTDSEMSU = record['fu_ftdsemsu']
    C1F.FTDANASW = record['fu_ftdanasw']
    C1F.FTDANAOW = record['fu_ftdanaow']
    C1F.FTDANATS = record['fu_ftdanats']
    C1F.FTDSENAS = record['fu_ftdsenas']
    C1F.FTDSENOS = record['fu_ftdsenos']
    C1F.FTDSENSR = record['fu_ftdsensr']
    C1F.FTDSENPR = record['fu_ftdsenpr']
    C1F.FTDNOUNC = record['fu_ftdnounc']
    C1F.FTDVERBC = record['fu_ftdverbc']
    C1F.FTDRATIO = record['fu_ftdratio']
    C1F.FTDREAAS = record['fu_ftdreaas']
    C1F.FTDREAOS = record['fu_ftdreaos']
    C1F.FTDREASR = record['fu_ftdreasr']
    C1F.FTDREAPR = record['fu_ftdreapr']
    packet.append(C1F)


def add_c2f(record, packet):
    C2F = ftld_fvp_forms.FormC2F()
    C2F.FTDCPC2F = record['fu_ftdcpc2f']
    C2F.FTDhAIRD = record['fu_ftdhaird']
    C2F.FTDSPIT  = record['fu_ftdspit']
    C2F.FTDNOSE  = record['fu_ftdnose']
    C2F.FTDCOAGE = record['fu_ftdcoage']
    C2F.FTDCRY   = record['fu_ftdcry']
    C2F.FTDCUT   = record['fu_ftdcut']
    C2F.FTDYTRIP = record['fu_ftdytrip']
    C2F.FTDEATP  = record['fu_ftdeatp']
    C2F.FTDTELLA = record['fu_ftdtella']
    C2F.FTDOPIN  = record['fu_ftdopin']
    C2F.FTDLAUGh = record['fu_ftdlaugh']
    C2F.FTDShIRT = record['fu_ftdshirt']
    C2F.FTDKEEPM = record['fu_ftdkeepm']
    C2F.FTDPICKN = record['fu_ftdpickn']
    C2F.FTDOVER  = record['fu_ftdover']
    C2F.FTDEATR  = record['fu_ftdeatr']
    C2F.FTDhAIRL = record['fu_ftdhairl']
    C2F.FTDShIRW = record['fu_ftdshirw']
    C2F.FTDMOVE  = record['fu_ftdmove']
    C2F.FTDhUGS  = record['fu_ftdhugs']
    C2F.FTDLOUD  = record['fu_ftdloud']
    C2F.FTDLOST  = record['fu_ftdlost']
    C2F.FTDSNTOT = record['fu_ftdsntot']
    C2F.FTDSNTBS = record['fu_ftdsntbs']
    C2F.FTDSNTOS = record['fu_ftdsntos']
    C2F.FTDSNRAT = record['fu_ftdsnrat']
    packet.append(C2F)


def add_c3f(record, packet):
    C3F = ftld_fvp_forms.FormC3F()
    C3F.FTDSELF  = record['fu_ftdself']
    C3F.FTDBADLY = record['fu_ftdbadly']
    C3F.FTDDEPR  = record['fu_ftddepr']
    C3F.FTDEMOTD = record['fu_ftdemotd']
    C3F.FTDLSELF = record['fu_ftdlself']
    C3F.FTDDISR  = record['fu_ftddisr']
    C3F.FTDBELCh = record['fu_ftdbelch']
    C3F.FTDGIGG  = record['fu_ftdgigg']
    C3F.FTDPRIV  = record['fu_ftdpriv']
    C3F.FTDNEGAT = record['fu_ftdnegat']
    C3F.FTDECOMM = record['fu_ftdecomm']
    C3F.FTDINAPJ = record['fu_ftdinapj']
    C3F.FTDFAILA = record['fu_ftdfaila']
    C3F.FTDRESIS = record['fu_ftdresis']
    C3F.FTDINTER = record['fu_ftdinter']
    C3F.FTDVERBA = record['fu_ftdverba']
    C3F.FTDPhYSI = record['fu_ftdphysi']
    C3F.FTDTOPIC = record['fu_ftdtopic']
    C3F.FTDPROTO = record['fu_ftdproto']
    C3F.FTDPREO  = record['fu_ftdpreo']
    C3F.FTDFINI  = record['fu_ftdfini']
    C3F.FTDACTED = record['fu_ftdacted']
    C3F.FTDABS   = record['fu_ftdabs']
    C3F.FTDFEEDB = record['fu_ftdfeedb']
    C3F.FTDFRUST = record['fu_ftdfrust']
    C3F.FTDANXI  = record['fu_ftdanxi']
    C3F.FTDNERVO = record['fu_ftdnervo']
    C3F.FTDNDIAG = record['fu_ftdndiag']
    C3F.FTDSTIMB = record['fu_ftdstimb']
    C3F.FTDSTIME = record['fu_ftdstime']
    C3F.FTDOBJEC = record['fu_ftdobjec']
    C3F.FTDCIRCU = record['fu_ftdcircu']
    C3F.FTDPERSE = record['fu_ftdperse']
    C3F.FTDREPEA = record['fu_ftdrepea']
    C3F.FTDANECD = record['fu_ftdanecd']
    C3F.FTDDINIT = record['fu_ftddinit']
    C3F.FTDDELAY = record['fu_ftddelay']
    C3F.FTDADDVE = record['fu_ftdaddve']
    C3F.FTDFLUCT = record['fu_ftdfluct']
    C3F.FTDLOSTT = record['fu_ftdlostt']
    C3F.FTDREPRU = record['fu_ftdrepru']
    C3F.FTDTRAIN = record['fu_ftdtrain']
    C3F.FTDDISCL = record['fu_ftddiscl']
    C3F.FTDSPONT = record['fu_ftdspont']
    C3F.FTDSPONR = record['fu_ftdsponr']
    C3F.FTDSTOOD = record['fu_ftdstood']
    C3F.FTDTOUCh = record['fu_ftdtouch']
    C3F.FTDDSOCI = record['fu_ftddsoci']
    C3F.FTDEXAGG = record['fu_ftdexagg']
    C3F.FTDSBTOT = record['fu_ftdsbtot']
    C3F.FTDSBCTO = record['fu_ftdsbcto']
    C3F.FTDLENGT = record['fu_ftdlengt']
    packet.append(C3F)


def add_c4f(record, packet):
    C4F = ftld_fvp_forms.FormC4F()
    C4F.FTDCPC4F = record['fu_ftdcpc4f']
    C4F.FTDWORKU = record['fu_ftdworku']
    C4F.FTDMIST  = record['fu_ftdmist']
    C4F.FTDCRIT  = record['fu_ftdcrit']
    C4F.FTDWORR  = record['fu_ftdworr']
    C4F.FTDBAD   = record['fu_ftdbad']
    C4F.FTDPOOR  = record['fu_ftdpoor']
    C4F.FTDFFEAR = record['fu_ftdffear']
    C4F.FTDBIST  = record['fu_ftdbist']
    packet.append(C4F)


def add_c5f(record, packet):
    C5F = ftld_fvp_forms.FormC5F()
    C5F.FTDCPC5F = record['fu_ftdcpc5f']
    C5F.FTDINSEX = record['fu_ftdinsex']
    C5F.FTDINFMO = record['fu_ftdinfmo']
    C5F.FTDINFYR = record['fu_ftdinfyr']
    C5F.FTDINFRE = record['fu_ftdinfre']
    C5F.FTDFEEL  = record['fu_ftdfeel']
    C5F.FTDDIFF  = record['fu_ftddiff']
    C5F.FTDSORR  = record['fu_ftdsorr']
    C5F.FTDSIDE  = record['fu_ftdside']
    C5F.FTDADVAN = record['fu_ftdadvan']
    C5F.FTDIMAG  = record['fu_ftdimag']
    C5F.FTDMISF  = record['fu_ftdmisf']
    C5F.FTDWASTE = record['fu_ftdwaste']
    C5F.FTDPITY  = record['fu_ftdpity']
    C5F.FTDQTOUC = record['fu_ftdqtouc']
    C5F.FTDSIDES = record['fu_ftdsides']
    C5F.FTDSOFTh = record['fu_ftdsofth']
    C5F.FTDUPSET = record['fu_ftdupset']
    C5F.FTDCRITI = record['fu_ftdcriti']
    C5F.FTDIRIEC = record['fu_ftdiriec']
    C5F.FTDIRIPT = record['fu_ftdiript']
    packet.append(C5F)


def add_c6f(record, packet):
    C6F = ftld_fvp_forms.FormC6F()
    C6F.FTDCPC6F = record['fu_ftdcpc6f']
    C6F.FTDALTER = record['fu_ftdalter']
    C6F.FTDEMOT  = record['fu_ftdemot']
    C6F.FTDACROS = record['fu_ftdacros']
    C6F.FTDCONV  = record['fu_ftdconv']
    C6F.FTDINTUI = record['fu_ftdintui']
    C6F.FTDJOKE  = record['fu_ftdjoke']
    C6F.FTDIMAGP = record['fu_ftdimagp']
    C6F.FTDINAPP = record['fu_ftdinapp']
    C6F.FTDChBEh = record['fu_ftdchbeh']
    C6F.FTDADBEh = record['fu_ftdadbeh']
    C6F.FTDLYING = record['fu_ftdlying']
    C6F.FTDGOODF = record['fu_ftdgoodf']
    C6F.FTDREGUL = record['fu_ftdregul']
    C6F.FTDSMSCR = record['fu_ftdsmscr']
    C6F.FTDSPSCR = record['fu_ftdspscr']
    C6F.FTDRSMST = record['fu_ftdrsmst']
    packet.append(C6F)


def add_e2f(record, packet):
    E2F = ftld_fvp_forms.FormE2F()
    E2F.FTDSMRI  = record['fu_ftdsmri']
    E2F.FTDSMMO  = record['fu_ftdsmmo']
    E2F.FTDSMDY  = record['fu_ftdsmdy']
    E2F.FTDSMYR  = record['fu_ftdsmyr']
    E2F.FTDSMDIC = record['fu_ftdsmdic']
    E2F.FTDSMDIS = record['fu_ftdsmdis']
    E2F.FTDSMADN = record['fu_ftdsmadn']
    E2F.FTDSMADV = record['fu_ftdsmadv']
    E2F.FTDSMMAN = record['fu_ftdsmman']
    E2F.FTDSMMAO = record['fu_ftdsmmao']
    E2F.FTDSMMAM = record['fu_ftdsmmam']
    E2F.FTDSMFS  = record['fu_ftdsmfs']
    E2F.FTDSMFSO = record['fu_ftdsmfso']
    E2F.FTDSMQU  = record['fu_ftdsmqu']
    E2F.FTDFDGPT = record['fu_ftdfdgpt']
    E2F.FTDFPMO  = record['fu_ftdfpmo']
    E2F.FTDFPDY  = record['fu_ftdfpdy']
    E2F.FTDFPYR  = record['fu_ftdfpyr']
    E2F.FTDFDDIC = record['fu_ftdfddic']
    E2F.FTDFDDID = record['fu_ftdfddid']
    E2F.FTDFDADN = record['fu_ftdfdadn']
    E2F.FTDFDADV = record['fu_ftdfdadv']
    E2F.FTDFDMAN = record['fu_ftdfdman']
    E2F.FTDFDMAO = record['fu_ftdfdmao']
    E2F.FTDFDMAM = record['fu_ftdfdmam']
    E2F.FTDFDQU  = record['fu_ftdfdqu']
    E2F.FTDAMYPT = record['fu_ftdamypt']
    E2F.FTDAMMO  = record['fu_ftdammo']
    E2F.FTDAMDY  = record['fu_ftdamdy']
    E2F.FTDAMYR  = record['fu_ftdamyr']
    E2F.FTDAMDIC = record['fu_ftdamdic']
    E2F.FTDAMDID = record['fu_ftdamdid']
    E2F.FTDAMLIG = record['fu_ftdamlig']
    E2F.FTDAMLIO = record['fu_ftdamlio']
    E2F.FTDAMADN = record['fu_ftdamadn']
    E2F.FTDAMADV = record['fu_ftdamadv']
    E2F.FTDAMMAN = record['fu_ftdamman']
    E2F.FTDAMMAO = record['fu_ftdammao']
    E2F.FTDAMMAM = record['fu_ftdammam']
    E2F.FTDAMQU  = record['fu_ftdamqu']
    E2F.FTDOThER = record['fu_ftdother']
    E2F.FTDOTDOP = record['fu_ftdotdop']
    E2F.FTDOTSER = record['fu_ftdotser']
    E2F.FTDOTChO = record['fu_ftdotcho']
    E2F.FTDOTANO = record['fu_ftdotano']
    E2F.FTDOTANS = record['fu_ftdotans']
    packet.append(E2F)


def add_e3f(record, packet):
    E3F = ftld_fvp_forms.FormE3F()
    E3F.FTDIDIAG = record['fu_ftdidiag']
    E3F.FTDSMRIO = record['fu_ftdsmrio']
    E3F.FTDMRIFA = record['fu_ftdmrifa']
    E3F.FTDMRIRF = record['fu_ftdmrirf']
    E3F.FTDMRILF = record['fu_ftdmrilf']
    E3F.FTDMRIRT = record['fu_ftdmrirt']
    E3F.FTDMRILT = record['fu_ftdmrilt']
    E3F.FTDMRIRM = record['fu_ftdmrirm']
    E3F.FTDMRILM = record['fu_ftdmrilm']
    E3F.FTDMRIRP = record['fu_ftdmrirp']
    E3F.FTDMRILP = record['fu_ftdmrilp']
    E3F.FTDMRIRB = record['fu_ftdmrirb']
    E3F.FTDMRILB = record['fu_ftdmrilb']
    E3F.FTDMRIOB = record['fu_ftdmriob']
    E3F.FTDMRIOS = record['fu_ftdmrios']
    E3F.FTDFDGPE = record['fu_ftdfdgpe']
    E3F.FTDFDGFh = record['fu_ftdfdgfh']
    E3F.FTDFDGRF = record['fu_ftdfdgrf']
    E3F.FTDFDGLF = record['fu_ftdfdglf']
    E3F.FTDFDGRT = record['fu_ftdfdgrt']
    E3F.FTDFDGLT = record['fu_ftdfdglt']
    E3F.FTDFDGRM = record['fu_ftdfdgrm']
    E3F.FTDFDGLM = record['fu_ftdfdglm']
    E3F.FTDFDGRP = record['fu_ftdfdgrp']
    E3F.FTDFDGLP = record['fu_ftdfdglp']
    E3F.FTDFDGRB = record['fu_ftdfdgrb']
    E3F.FTDFDGLB = record['fu_ftdfdglb']
    E3F.FTDFDGOA = record['fu_ftdfdgoa']
    E3F.FTDFDGOS = record['fu_ftdfdgos']
    E3F.FTDAMYP  = record['fu_ftdamyp']
    E3F.FTDAMYVI = record['fu_ftdamyvi']
    E3F.FTDAMYRF = record['fu_ftdamyrf']
    E3F.FTDAMYLF = record['fu_ftdamylf']
    E3F.FTDAMYRT = record['fu_ftdamyrt']
    E3F.FTDAMYLT = record['fu_ftdamylt']
    E3F.FTDAMYRM = record['fu_ftdamyrm']
    E3F.FTDAMYLM = record['fu_ftdamylm']
    E3F.FTDAMYRP = record['fu_ftdamyrp']
    E3F.FTDAMYLP = record['fu_ftdamylp']
    E3F.FTDAMYRB = record['fu_ftdamyrb']
    E3F.FTDAMYLB = record['fu_ftdamylb']
    E3F.FTDAMYOA = record['fu_ftdamyoa']
    E3F.FTDAMYOS = record['fu_ftdamyos']
    E3F.FTDCBFSP = record['fu_ftdcbfsp']
    E3F.FTDCBFVI = record['fu_ftdcbfvi']
    E3F.FTDCBFRF = record['fu_ftdcbfrf']
    E3F.FTDCBFLF = record['fu_ftdcbflf']
    E3F.FTDCBFRT = record['fu_ftdcbfrt']
    E3F.FTDCBFLT = record['fu_ftdcbflt']
    E3F.FTDCBFRM = record['fu_ftdcbfrm']
    E3F.FTDCBFLM = record['fu_ftdcbflm']
    E3F.FTDCBFRP = record['fu_ftdcbfrp']
    E3F.FTDCBFLP = record['fu_ftdcbflp']
    E3F.FTDCBFRB = record['fu_ftdcbfrb']
    E3F.FTDCBFLB = record['fu_ftdcbflb']
    E3F.FTDCBFOA = record['fu_ftdcbfoa']
    E3F.FTDCBFOS = record['fu_ftdcbfos']
    E3F.FTDOTHI  = record['fu_ftdothi']
    E3F.FTDOTHIS = record['fu_ftdothis']
    packet.append(E3F)


def update_header(record, packet):
    for header in packet:
        header.PACKET = "FF"
        header.FORMID = header.form_name
        if header.FORMID == "Z1X":
            header.PACKET = "F"
        header.FORMVER = 3
        header.ADCID = record['adcid']
        header.PTID = record['ptid']
        header.VISITMO = record['visitmo']
        header.VISITDAY = record['visitday']
        header.VISITYR = record['visityr']
        header.VISITNUM = record['visitnum']
        header.INITIALS = record['initials']
