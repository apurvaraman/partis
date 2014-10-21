""" A few utility functions. At the moment simply functions used in recombinator which do not
require member variables. """

import sys
import os
import re
import math
import glob
import collections
import csv
from scipy.stats import beta

from opener import opener

from Bio import SeqIO

#----------------------------------------------------------------------------------------
eps = 1.0e-10  # if things that should be 1.0 are this close to 1.0, blithely keep on keepin on. kinda arbitrary, but works for the moment. TODO actually replace the 1e-8s and 1e-10s with this constant
def is_normed(prob):
    return math.fabs(prob - 1.0) < eps  #*1000000000

# ----------------------------------------------------------------------------------------
regions = ['v', 'd', 'j']
erosions = ['v_3p', 'd_5p', 'd_3p', 'j_5p']
boundaries = ('vd', 'dj')
humans = ('A', 'B', 'C')
nukes = ('A', 'C', 'G', 'T')
maturities = ['memory', 'naive']  # NOTE eveywhere else I call this 'naivety' and give it the values 'M' or 'N'
naivities = ['M', 'N']
conserved_codon_names = {'v':'cyst', 'd':'', 'j':'tryp'}
# Infrastrucure to allow hashing all the columns together into a dict key.
# Uses a tuple with the variables that are used to index selection frequencies
index_columns = ('v_gene', 'd_gene', 'j_gene', 'cdr3_length', 'v_3p_del', 'd_5p_del', 'd_3p_del', 'j_5p_del', 'vd_insertion', 'dj_insertion')
index_keys = {}
for i in range(len(index_columns)):  # dict so we can access them by name instead of by index number
    index_keys[index_columns[i]] = i

all_gene_tuple = ('IGHD1-1*01', 'IGHD1-14*01', 'IGHD1-20*01', 'IGHD1-26*01', 'IGHD1-7*01', 'IGHD1/OR15-1a*01', 'IGHD1/OR15-1b*01', 'IGHD2-15*01', 'IGHD2-2*01', 'IGHD2-2*02', 'IGHD2-2*03', 'IGHD2-21*01', 'IGHD2-21*02', 'IGHD2-8*01', 'IGHD2-8*02', 'IGHD2/OR15-2a*01', 'IGHD2/OR15-2b*01', 'IGHD3-10*01', 'IGHD3-10*02', 'IGHD3-16*01', 'IGHD3-16*02', 'IGHD3-22*01', 'IGHD3-3*01', 'IGHD3-3*02', 'IGHD3-9*01', 'IGHD3/OR15-3a*01', 'IGHD3/OR15-3b*01', 'IGHD4-11*01', 'IGHD4-17*01', 'IGHD4-23*01', 'IGHD4-4*01', 'IGHD4/OR15-4a*01', 'IGHD4/OR15-4b*01', 'IGHD5-12*01', 'IGHD5-18*01', 'IGHD5-24*01', 'IGHD5-5*01', 'IGHD5/OR15-5a*01', 'IGHD5/OR15-5b*01', 'IGHD6-13*01', 'IGHD6-19*01', 'IGHD6-25*01', 'IGHD6-6*01', 'IGHD7-27*01', 'IGHJ1*01_F', 'IGHJ1P*01_P', 'IGHJ2*01_F', 'IGHJ2P*01_P', 'IGHJ3*01_F', 'IGHJ3*02_F', 'IGHJ3P*01_P', 'IGHJ3P*02_P', 'IGHJ4*01_F', 'IGHJ4*02_F', 'IGHJ4*03_F', 'IGHJ5*01_F', 'IGHJ5*02_F', 'IGHJ6*01_F', 'IGHJ6*02_F', 'IGHJ6*03_F', 'IGHJ6*04_F', 'IGHV1-18*01', 'IGHV1-18*03', 'IGHV1-2*01', 'IGHV1-2*02', 'IGHV1-2*03', 'IGHV1-2*04', 'IGHV1-2*05', 'IGHV1-24*01', 'IGHV1-3*01', 'IGHV1-3*02', 'IGHV1-45*01', 'IGHV1-45*02', 'IGHV1-45*03', 'IGHV1-46*01', 'IGHV1-46*02', 'IGHV1-46*03', 'IGHV1-58*01', 'IGHV1-58*02', 'IGHV1-68*01', 'IGHV1-69*01', 'IGHV1-69*02', 'IGHV1-69*04', 'IGHV1-69*05', 'IGHV1-69*06', 'IGHV1-69*08', 'IGHV1-69*09', 'IGHV1-69*10', 'IGHV1-69*11', 'IGHV1-69*12', 'IGHV1-69*13', 'IGHV1-8*01', 'IGHV1-8*02', 'IGHV1-NL1*01', 'IGHV1-c*01', 'IGHV1-f*01', 'IGHV1/OR15-1*01', 'IGHV1/OR15-1*02', 'IGHV1/OR15-1*03', 'IGHV1/OR15-1*04', 'IGHV1/OR15-2*01', 'IGHV1/OR15-2*02', 'IGHV1/OR15-2*03', 'IGHV1/OR15-3*01', 'IGHV1/OR15-3*02', 'IGHV1/OR15-3*03', 'IGHV1/OR15-4*01', 'IGHV1/OR15-5*01', 'IGHV1/OR15-5*02', 'IGHV1/OR15-9*01', 'IGHV1/OR21-1*01', 'IGHV2-10*01', 'IGHV2-26*01', 'IGHV2-5*01', 'IGHV2-5*04', 'IGHV2-5*05', 'IGHV2-5*06', 'IGHV2-5*07', 'IGHV2-5*08', 'IGHV2-5*09', 'IGHV2-5*10', 'IGHV2-70*01', 'IGHV2-70*09', 'IGHV2-70*10', 'IGHV2-70*11', 'IGHV2-70*12', 'IGHV2-70*13', 'IGHV2/OR16-5*01', 'IGHV3-11*01', 'IGHV3-11*03', 'IGHV3-11*04', 'IGHV3-11*05', 'IGHV3-13*01', 'IGHV3-13*02', 'IGHV3-13*03', 'IGHV3-13*04', 'IGHV3-15*01', 'IGHV3-15*02', 'IGHV3-15*03', 'IGHV3-15*04', 'IGHV3-15*05', 'IGHV3-15*06', 'IGHV3-15*07', 'IGHV3-15*08', 'IGHV3-16*01', 'IGHV3-16*02', 'IGHV3-19*01', 'IGHV3-20*01', 'IGHV3-21*01', 'IGHV3-21*02', 'IGHV3-21*03', 'IGHV3-21*04', 'IGHV3-22*01', 'IGHV3-22*02', 'IGHV3-23*01', 'IGHV3-23*02', 'IGHV3-23*03', 'IGHV3-23*04', 'IGHV3-25*01', 'IGHV3-25*02', 'IGHV3-25*03', 'IGHV3-25*04', 'IGHV3-25*05', 'IGHV3-30*01', 'IGHV3-30*02', 'IGHV3-30*03', 'IGHV3-30*04', 'IGHV3-30*05', 'IGHV3-30*06', 'IGHV3-30*07', 'IGHV3-30*08', 'IGHV3-30*09', 'IGHV3-30*10', 'IGHV3-30*11', 'IGHV3-30*12', 'IGHV3-30*13', 'IGHV3-30*14', 'IGHV3-30*15', 'IGHV3-30*16', 'IGHV3-30*17', 'IGHV3-30*18', 'IGHV3-30*19', 'IGHV3-30-3*01', 'IGHV3-30-3*02', 'IGHV3-32*01', 'IGHV3-33*01', 'IGHV3-33*02', 'IGHV3-33*03', 'IGHV3-33*04', 'IGHV3-33*05', 'IGHV3-33*06', 'IGHV3-35*01', 'IGHV3-38*01', 'IGHV3-38*02', 'IGHV3-43*01', 'IGHV3-43*02', 'IGHV3-47*01', 'IGHV3-47*02', 'IGHV3-48*01', 'IGHV3-48*02', 'IGHV3-48*03', 'IGHV3-48*04', 'IGHV3-49*01', 'IGHV3-49*02', 'IGHV3-49*03', 'IGHV3-49*04', 'IGHV3-49*05', 'IGHV3-52*01', 'IGHV3-53*01', 'IGHV3-53*02', 'IGHV3-53*03', 'IGHV3-53*04', 'IGHV3-54*01', 'IGHV3-54*02', 'IGHV3-54*04', 'IGHV3-62*01', 'IGHV3-63*01', 'IGHV3-63*02', 'IGHV3-64*01', 'IGHV3-64*02', 'IGHV3-64*03', 'IGHV3-64*04', 'IGHV3-64*05', 'IGHV3-66*01', 'IGHV3-66*02', 'IGHV3-66*03', 'IGHV3-66*04', 'IGHV3-7*01', 'IGHV3-7*02', 'IGHV3-7*03', 'IGHV3-71*01', 'IGHV3-71*02', 'IGHV3-71*03', 'IGHV3-72*01', 'IGHV3-73*01', 'IGHV3-73*02', 'IGHV3-74*01', 'IGHV3-74*02', 'IGHV3-74*03', 'IGHV3-9*01', 'IGHV3-9*02', 'IGHV3-NL1*01', 'IGHV3-d*01', 'IGHV3-h*01', 'IGHV3-h*02', 'IGHV3/OR15-7*01', 'IGHV3/OR15-7*02', 'IGHV3/OR15-7*03', 'IGHV3/OR15-7*05', 'IGHV3/OR16-10*01', 'IGHV3/OR16-10*02', 'IGHV3/OR16-10*03', 'IGHV3/OR16-12*01', 'IGHV3/OR16-13*01', 'IGHV3/OR16-14*01', 'IGHV3/OR16-15*01', 'IGHV3/OR16-15*02', 'IGHV3/OR16-16*01', 'IGHV3/OR16-6*02', 'IGHV3/OR16-8*01', 'IGHV3/OR16-8*02', 'IGHV3/OR16-9*01', 'IGHV4-28*01', 'IGHV4-28*02', 'IGHV4-28*03', 'IGHV4-28*04', 'IGHV4-28*06', 'IGHV4-30-2*01', 'IGHV4-30-2*02', 'IGHV4-30-2*03', 'IGHV4-30-2*04', 'IGHV4-30-2*05', 'IGHV4-30-4*01', 'IGHV4-30-4*02', 'IGHV4-30-4*05', 'IGHV4-30-4*06', 'IGHV4-31*01', 'IGHV4-31*02', 'IGHV4-31*03', 'IGHV4-31*04', 'IGHV4-31*05', 'IGHV4-31*10', 'IGHV4-34*01', 'IGHV4-34*02', 'IGHV4-34*04', 'IGHV4-34*05', 'IGHV4-34*08', 'IGHV4-34*09', 'IGHV4-34*10', 'IGHV4-34*11', 'IGHV4-34*12', 'IGHV4-34*13', 'IGHV4-39*01', 'IGHV4-39*02', 'IGHV4-39*05', 'IGHV4-39*06', 'IGHV4-39*07', 'IGHV4-4*01', 'IGHV4-4*02', 'IGHV4-4*06', 'IGHV4-4*07', 'IGHV4-55*01', 'IGHV4-55*02', 'IGHV4-55*08', 'IGHV4-55*09', 'IGHV4-59*01', 'IGHV4-59*02', 'IGHV4-59*03', 'IGHV4-59*04', 'IGHV4-59*05', 'IGHV4-59*06', 'IGHV4-59*07', 'IGHV4-59*08', 'IGHV4-59*09', 'IGHV4-59*10', 'IGHV4-61*01', 'IGHV4-61*02', 'IGHV4-61*03', 'IGHV4-61*05', 'IGHV4-61*06', 'IGHV4-61*07', 'IGHV4-61*08', 'IGHV4-b*01', 'IGHV4-b*02', 'IGHV4/OR15-8*01', 'IGHV4/OR15-8*02', 'IGHV4/OR15-8*03', 'IGHV5-51*01', 'IGHV5-51*02', 'IGHV5-51*03', 'IGHV5-51*04', 'IGHV5-78*01', 'IGHV5-a*01', 'IGHV5-a*02', 'IGHV5-a*03', 'IGHV5-a*04', 'IGHV6-1*01', 'IGHV6-1*02', 'IGHV7-34-1*02', 'IGHV7-4-1*01', 'IGHV7-4-1*02', 'IGHV7-4-1*04', 'IGHV7-4-1*05', 'IGHV7-40*03', 'IGHV7-81*01', 'IGHV1-8*91', 'IGHV1-NL1*91', 'IGHV2-5*91', 'IGHV3-20*91', 'IGHV3-43*91', 'IGHV3-53*91', 'IGHV3-9*91', 'IGHV4-30-2*91', 'IGHV7-4-1*91', 'IGHV7-4-1*92', 'IGHV1-3*91', 'IGHV3-64*91', 'IGHV3/OR16-13*91', 'IGHV3/OR16-14*91', 'IGHV7-4-1*93', 'IGHV4-39*91', 'IGHV4-4*91', 'IGHV4-59*91')

# ----------------------------------------------------------------------------------------
# Info specifying which parameters are assumed to correlate with which others. Taken from mutual
# information plot in bcellap repo

# key is parameter of interest, and associated list gives the parameters (other than itself) which are necessary to predict it
column_dependencies = {}
column_dependencies['v_gene'] = [] # TODO v choice actually depends on everything... but not super strongly, so a.t.m. I ignore it
column_dependencies['v_3p_del'] = ['v_gene']
column_dependencies['d_gene'] = []  # ['d_5p_del', 'd_3p_del'] TODO stop ignoring this correlation. Well, maybe. See note in hmmwriter.py
column_dependencies['d_5p_del'] = ['d_3p_del', 'd_gene']  # NOTE at least for now there's no way to specify the d erosion correlations
column_dependencies['d_3p_del'] = ['d_5p_del', 'd_gene']  #   in the hmm, so they're integrated out
column_dependencies['j_gene'] = []  # ['dj_insertion']  TODO see note above
column_dependencies['j_5p_del'] = [] # strange but seemingly true: does not depend on j choice. NOTE this makes normalization kinda fun when you read these out
column_dependencies['vd_insertion'] = []
column_dependencies['dj_insertion'] = ['j_gene']

# tuples with the column and its dependencies mashed together
# (first entry is the column of interest, and it depends upon the following entries)
column_dependency_tuples = []
for column, deps in column_dependencies.iteritems():
    tmp_list = [column]
    tmp_list.extend(deps)
    column_dependency_tuples.append(tuple(tmp_list))

def get_parameter_fname(column=None, deps=None, column_and_deps=None):
    """ return the file name in which we store the information for <column>. Either pass in <column> and <deps> *or* <column_and_deps> """
    if column == 'all':
        return 'all-probs.csv'
    if column_and_deps == None:
        column_and_deps = [column]
        column_and_deps.extend(deps)
    outfname = 'probs.csv'
    for ic in column_and_deps:
        outfname = ic + '-' + outfname
    return outfname

# ----------------------------------------------------------------------------------------
# bash color codes
Colors = {}
Colors['head'] = '\033[95m'
Colors['bold'] = '\033[1m'
Colors['purple'] = '\033[95m'
Colors['blue'] = '\033[94m'
Colors['green'] = '\033[92m'
Colors['yellow'] = '\033[93m'
Colors['red'] = '\033[91m'
Colors['end'] = '\033[0m'

def color(col, seq):
    assert col in Colors
    return Colors[col] + seq + Colors['end']

# ----------------------------------------------------------------------------------------
def color_mutants(ref_seq, seq, print_result=False):
    assert len(ref_seq) == len(seq)
    return_str = ''
    for inuke in range(len(seq)):
        if inuke >= len(ref_seq) or seq[inuke] == ref_seq[inuke]:
            return_str += seq[inuke]
        else:
            return_str += color('red', seq[inuke])
    if print_result:
        print '%0s %s' % ('', ref_seq)
        print '%0s %s' % ('', return_str)
    return return_str

# ----------------------------------------------------------------------------------------
def color_gene(gene):
    """ color gene name (and remove extra characters), eg IGHV3-h*01 --> v 3-h 1 """
    return_str = gene[:3] + color('bold', color('red', gene[3])) + ' '  # add a space after
    n_version = gene[4 : gene.find('-')]
    n_subversion = gene[gene.find('-')+1 : gene.find('*')]
    if get_region(gene) == 'j':
        n_version = gene[4 : gene.find('*')]
        n_subversion = ''
        return_str += color('purple', n_version)
    else:
        return_str += color('purple', n_version) + '-' + color('purple', n_subversion)

    if gene.find('*') != -1:
        allele_end = gene.find('_')
        if allele_end < 0:
            allele_end = len(gene)
        allele = gene[gene.find('*')+1 : allele_end]
        return_str += '*' + color('yellow', allele)
        if '_' in gene:  # _F or _P in j gene names
            return_str += gene[gene.find('_') :]

    # now remove extra characters
    return_str = return_str.replace('IGH','  ').lower()
    return_str = return_str.replace('*',' ')
    return return_str

#----------------------------------------------------------------------------------------
def int_to_nucleotide(number):
    """ Convert between (0,1,2,3) and (A,C,G,T) """
    if number == 0:
        return 'A'
    elif number == 1:
        return 'C'
    elif number == 2:
        return 'G'
    elif number == 3:
        return 'T'
    else:
        print 'ERROR nucleotide number not in [0,3]'
        sys.exit()

# ----------------------------------------------------------------------------------------                    
def check_conserved_cysteine(seq, cyst_position, debug=False, extra_str=''):
    """ Ensure there's a cysteine at <cyst_position> in <seq>. """
    if len(seq) < cyst_position+3:
        if debug:
            print '%sERROR seq not long enough in cysteine checker %d %s' % (extra_str, cyst_position, seq)
        assert False
    cyst_word = str(seq[cyst_position:cyst_position+3])
    if cyst_word != 'TGT' and cyst_word != 'TGC':
        if debug:
            print '%sERROR cysteine in v is messed up: %s (%s %d)' % (extra_str, cyst_word, seq, cyst_position)
        assert False

# ----------------------------------------------------------------------------------------
def check_conserved_tryptophan(seq, tryp_position, debug=False, extra_str=''):
    """ Ensure there's a tryptophan at <tryp_position> in <seq>. """
    if len(seq) < tryp_position+3:
        if debug:
            print '%sERROR seq not long enough in tryp checker %d %s' % (extra_str, tryp_position, seq)
        assert False
    tryp_word = str(seq[tryp_position:tryp_position+3])
    if tryp_word != 'TGG':
        if debug:
            print '%sERROR tryptophan in j is messed up: %s (%s %d)' % (extra_str, tryp_word, seq, tryp_position)
        assert False

# ----------------------------------------------------------------------------------------
def check_both_conserved_codons(seq, cyst_position, tryp_position, debug=False, extra_str=''):
    """ Double check that we conserved the cysteine and the tryptophan. """
    check_conserved_cysteine(seq, cyst_position, debug, extra_str=extra_str)
    check_conserved_tryptophan(seq, tryp_position, debug, extra_str=extra_str)

# ----------------------------------------------------------------------------------------
def are_conserved_codons_screwed_up(reco_event):
    """ Version that checks all the final seqs in reco_event.

    Returns True if codons are screwed up, or if no sequences have been added.
    """
    if len(reco_event.final_seqs) == 0:
        return True
    for seq in reco_event.final_seqs:
        try:
            check_both_conserved_codons(seq, reco_event.cyst_position, reco_event.final_tryp_position)
        except AssertionError:
            return True

    return False

#----------------------------------------------------------------------------------------
def check_for_stop_codon(seq, cyst_position):
    """ make sure there is no in-frame stop codon, where frame is inferred from <cyst_position> """
    assert cyst_position < len(seq)
    # jump leftward in steps of three until we reach the start of the sequence
    ipos = cyst_position
    while ipos > 2:
        ipos -= 3
    # ipos should now bet the index of the start of the first complete codon
    while ipos + 2 < len(seq):  # then jump forward in steps of three bases making sure none of them are stop codons
        codon = seq[ipos:ipos+3]
        if codon == 'TAG' or codon == 'TAA' or codon == 'TGA':
            print '      ERROR stop codon %s at %d in %s' % (codon, ipos, seq)
            assert False
        ipos += 3

#----------------------------------------------------------------------------------------
def is_position_protected(protected_positions, prospective_position):
    """ Would a mutation at <prospective_position> screw up a protected codon? """
    for position in protected_positions:
        if (prospective_position == position or
            prospective_position == (position + 1) or
            prospective_position == (position + 2)):
            return True
    return False

#----------------------------------------------------------------------------------------
def would_erode_conserved_codon(reco_event):
    """ Would any of the erosion <lengths> delete a conserved codon? """
    lengths = reco_event.erosions
    # check conserved cysteine
    if len(reco_event.seqs['v']) - lengths['v_3p'] <= reco_event.cyst_position + 2:
        print '      about to erode cysteine (%d), try again' % lengths['v_3p']
        return True  # i.e. it *would* screw it up
    # check conserved tryptophan
    if lengths['j_5p'] - 1 >= reco_event.tryp_position:
        print '      about to erode tryptophan (%d), try again' % lengths['j_5p']
        return True

    return False  # *whew*, it won't erode either of 'em

#----------------------------------------------------------------------------------------
def is_erosion_longer_than_seq(reco_event):
    """ Are any of the proposed erosion <lengths> longer than the seq to be eroded? """
    lengths = reco_event.erosions
    if lengths['v_3p'] > len(reco_event.seqs['v']):  # NOTE not actually possible since we already know we didn't erode the cysteine
        print '      v_3p erosion too long (%d)' % lengths['v_3p']
        return True
    if lengths['d_5p'] + lengths['d_3p'] > len(reco_event.seqs['d']):
        print '      d erosions too long (%d)' % (lengths['d_5p'] + lengths['d_3p'])
        return True
    if lengths['j_5p'] > len(reco_event.seqs['j']):  # NOTE also not possible for the same reason
        print '      j_5p erosion too long (%d)' % lengths['j_5p']
        return True
    return False

#----------------------------------------------------------------------------------------
def find_tryp_in_joined_seq(gl_tryp_position_in_j, v_seq, vd_insertion, d_seq, dj_insertion, j_seq, j_erosion, debug=False):
    """ Find the <end> tryptophan in a joined sequence.

    Given local tryptophan position in the j region, figure
    out what position it's at in the final sequence.
    NOTE gl_tryp_position_in_j is the position *before* the j was eroded,
    but this fcn assumes that the j *has* been eroded.
    also NOTE <[vdj]_seq> are assumed to already be eroded
    """
    if debug:
        print 'checking tryp with: %s, %d - %d = %d' % (j_seq, gl_tryp_position_in_j, j_erosion, gl_tryp_position_in_j - j_erosion)
    check_conserved_tryptophan(j_seq, gl_tryp_position_in_j - j_erosion)  # make sure tryp is where it's supposed to be
    length_to_left_of_j = len(v_seq + vd_insertion + d_seq + dj_insertion)
    if debug:
        print '  finding tryp position as'
        print '    length_to_left_of_j = len(v_seq + vd_insertion + d_seq + dj_insertion) = %d + %d + %d + %d' % (len(v_seq), len(vd_insertion), len(d_seq), len(dj_insertion))
        print '    result = gl_tryp_position_in_j - j_erosion + length_to_left_of_j = %d - %d + %d = %d' % (gl_tryp_position_in_j, j_erosion, length_to_left_of_j, gl_tryp_position_in_j - j_erosion + length_to_left_of_j)
    return gl_tryp_position_in_j - j_erosion + length_to_left_of_j

# ----------------------------------------------------------------------------------------
def is_mutated(original, final, n_muted=-1, n_total=-1):
    n_total += 1
    return_str = final
    if original != final:
        return_str = color('red', final)
        n_muted += 1
    return return_str, n_muted, n_total

# ----------------------------------------------------------------------------------------
def get_v_5p_del(original_seqs, line):
    # deprecated
    assert False  # this method will no longer work when I need to get v left *and* j right 'deletions'
    original_length = len(original_seqs['v']) + len(original_seqs['d']) + len(original_seqs['j'])
    total_deletion_length = int(line['v_3p_del']) + int(line['d_5p_del']) + int(line['d_3p_del']) + int(line['j_5p_del'])
    total_insertion_length = len(line['vd_insertion']) + len(line['dj_insertion'])
    return original_length - total_deletion_length + total_insertion_length - len(line['seq'])

# ----------------------------------------------------------------------------------------
def get_reco_event_seqs(germlines, line, original_seqs, lengths, eroded_seqs):
    """
    get original and eroded germline seqs
    damn these function names kinda suck. TODO rejigger the function and variable names hereabouts
    """
    for region in regions:
        del_5p = int(line[region + '_5p_del'])
        del_3p = int(line[region + '_3p_del'])
        original_seqs[region] = germlines[region][line[region + '_gene']]
        lengths[region] = len(original_seqs[region]) - del_5p - del_3p
        # assert del_5p + lengths[region] != 0
        eroded_seqs[region] = original_seqs[region][del_5p : del_5p + lengths[region]]


# ----------------------------------------------------------------------------------------
def get_conserved_codon_position(cyst_positions, tryp_positions, region, gene, glbounds, qrbounds):
    """
    Find location of the conserved cysteine/tryptophan in a query sequence given a germline match which is specified by
    its germline bounds <glbounds> and its bounds in the query sequence <qrbounds>
    """
    # NOTE see add_cdr3_info -- they do similar things, but start from different information
    if region == 'v':
        gl_cpos = cyst_positions[gene]['cysteine-position']  # germline cysteine position
        query_cpos = gl_cpos - glbounds[0] + qrbounds[0]  # cysteine position in query sequence match
        return query_cpos
    elif region == 'j':
        gl_tpos = int(tryp_positions[gene])
        query_tpos = gl_tpos - glbounds[0] + qrbounds[0]
        return query_tpos
    else:
        return -1
# ----------------------------------------------------------------------------------------
def add_cdr3_info(cyst_positions, tryp_positions, line, eroded_seqs):
    """ Add the cyst_position, tryp_position, and cdr3_length to <line> based on the information already in <line> """
    # NOTE see get_conserved_codon_position -- they do similar things, but start from different information
    eroded_gl_cpos = cyst_positions[line['v_gene']]['cysteine-position'] - int(line['v_5p_del'])  # cysteine position in eroded germline sequence
    eroded_gl_tpos = int(tryp_positions[line['j_gene']]) - int(line['j_5p_del'])
    try:
        line['cyst_position'] = eroded_gl_cpos
        tpos_in_joined_seq = eroded_gl_tpos + len(eroded_seqs['v']) + len(line['vd_insertion']) + len(eroded_seqs['d']) + len(line['dj_insertion'])
        line['tryp_position'] = tpos_in_joined_seq
        line['cdr3_length'] = tpos_in_joined_seq - eroded_gl_cpos + 3
        check_conserved_cysteine(eroded_seqs['v'], eroded_gl_cpos, debug=True, extra_str='      ')
        check_conserved_tryptophan(eroded_seqs['j'], eroded_gl_tpos, debug=True, extra_str='      ')
    except AssertionError:
        print '    bad codon, setting cdr3_length to -1'
        line['cdr3_length'] = -1
    
# ----------------------------------------------------------------------------------------
def get_full_naive_seq(germlines, line):
    original_seqs = {}  # original (non-eroded) germline seqs
    lengths = {}  # length of each match (including erosion)
    eroded_seqs = {}  # eroded germline seqs
    get_reco_event_seqs(germlines, line, original_seqs, lengths, eroded_seqs)
    return eroded_seqs['v'] + line['vd_insertion'] + eroded_seqs['d'] + line['dj_insertion'] + eroded_seqs['j']

# ----------------------------------------------------------------------------------------
def add_match_info(germlines, line, cyst_positions, tryp_positions, skip_unproductive):
    """
    add to <line> the query match seqs (sections of the query sequence that are matched to germline) and their corresponding germline matches.

    """

    original_seqs = {}  # original (non-eroded) germline seqs
    lengths = {}  # length of each match (including erosion)
    eroded_seqs = {}  # eroded germline seqs
    get_reco_event_seqs(germlines, line, original_seqs, lengths, eroded_seqs)
    add_cdr3_info(cyst_positions, tryp_positions, line, eroded_seqs)  # add cyst and tryp positions, and cdr3 length

    # add the <eroded_seqs> to <line> so we can find them later
    for region in regions:
        line[region + '_gl_seq'] = eroded_seqs[region]

    # the sections of the query sequence which are assigned to each region
    d_start = len(eroded_seqs['v']) + len(line['vd_insertion'])
    j_start = d_start + len(eroded_seqs['d']) + len(line['dj_insertion'])
    line['v_qr_seq'] = line['seq'][:len(eroded_seqs['v'])]
    line['d_qr_seq'] = line['seq'][d_start : d_start + len(eroded_seqs['d'])]
    line['j_qr_seq'] = line['seq'][j_start : j_start + len(eroded_seqs['j'])]

# ----------------------------------------------------------------------------------------
def print_reco_event(germlines, line, one_line=False, extra_str=''):
    """ Print ascii summary of recombination event and mutation.

    If <one_line>, then only print out the final_seq line.
    """
    
    v_5p_del = int(line['v_5p_del'])
    v_3p_del = int(line['v_3p_del'])
    d_5p_del = int(line['d_5p_del'])
    d_3p_del = int(line['d_3p_del'])
    j_5p_del = int(line['j_5p_del'])
    j_3p_del = int(line['j_3p_del'])

    original_seqs = {}  # original (non-eroded) germline seqs
    lengths = {}  # length of each match (including erosion)
    eroded_seqs = {}  # eroded germline seqs
    get_reco_event_seqs(germlines, line, original_seqs, lengths, eroded_seqs)

    germline_v_end = len(original_seqs['v']) - v_5p_del - 1  # position in the query sequence at which we find the last base of the v match. NOTE we subtract off the v_5p_del because we're *not* adding dots for that deletion (it's just too long)
    germline_d_start = lengths['v'] + len(line['vd_insertion']) - d_5p_del
    germline_d_end = germline_d_start + len(original_seqs['d'])
    germline_j_start = germline_d_end + 1 - d_3p_del + len(line['dj_insertion']) - j_5p_del

    final_seq = ''
    n_muted, n_total = 0, 0
    j_right_extra = ''  # portion of query sequence to right of end of the j match
    # TODO allow v match to start to right of start of query sequence
    for inuke in range(len(line['seq'])):  # - j_3p_del):
        ilocal = inuke
        new_nuke = ''
        if ilocal < lengths['v']:
            new_nuke, n_muted, n_total = is_mutated(eroded_seqs['v'][ilocal], line['seq'][inuke], n_muted, n_total)
        else:
            ilocal -= lengths['v']
            if ilocal < len(line['vd_insertion']):
                new_nuke, n_muted, n_total = is_mutated(line['vd_insertion'][ilocal], line['seq'][inuke], n_muted, n_total)
            else:
                ilocal -= len(line['vd_insertion'])
                if ilocal < lengths['d']:
                    new_nuke, n_muted, n_total = is_mutated(eroded_seqs['d'][ilocal], line['seq'][inuke], n_muted, n_total)
                else:
                    ilocal -= lengths['d']
                    if ilocal < len(line['dj_insertion']):
                        new_nuke, n_muted, n_total = is_mutated(line['dj_insertion'][ilocal], line['seq'][inuke], n_muted, n_total)
                    else:
                        ilocal -= len(line['dj_insertion'])
                        if ilocal < lengths['j']:
                            new_nuke, n_muted, n_total = is_mutated(eroded_seqs['j'][ilocal], line['seq'][inuke], n_muted, n_total)
                        else:
                            new_nuke, n_muted, n_total = line['seq'][inuke], n_muted, n_total+1
                            j_right_extra += ' '

        if 'cyst_position' in line and 'tryp_position' in line:
            for pos in (line['cyst_position'], line['tryp_position']):  # reverse video for the conserved codon positions
                # adjusted_pos = pos - v_5p_del  # adjust positions to allow for reads not extending all the way to left side of v
                adjusted_pos = pos  # don't need to subtract it for smith-waterman stuff... gr, need to make it general
                if inuke >= adjusted_pos and inuke < adjusted_pos+3:
                    new_nuke = '\033[7m' + new_nuke + '\033[m'

        final_seq += new_nuke

    # check if there isn't enough space for dots in the vj line
    no_space = False
    if v_3p_del + j_5p_del > len(line['vd_insertion']) + len(eroded_seqs['d']) + len(line['dj_insertion']):
        no_space = True

    eroded_seqs_dots = {}
    eroded_seqs_dots['v'] = eroded_seqs['v'] + v_3p_del * '.'
    eroded_seqs_dots['d'] = d_5p_del * '.' + eroded_seqs['d'] + d_3p_del * '.'
    eroded_seqs_dots['j'] = j_5p_del * '.' + eroded_seqs['j'] + j_3p_del * '.'

    insertions = ' ' * lengths['v']
    insertions += line['vd_insertion']
    insertions += ' ' * lengths['d']
    insertions += line['dj_insertion']
    insertions += ' ' * lengths['j']
    insertions += j_right_extra
    insertions += ' ' * j_3p_del

    d_line = ' ' * germline_d_start  # len(original_seqs['j']) - j_5p_del - j_3p_del
    d_line += eroded_seqs_dots['d']
    d_line += ' ' * (len(original_seqs['j']) - j_5p_del - j_3p_del + len(line['dj_insertion']) - d_3p_del)
    d_line += j_right_extra
    d_line += ' ' * j_3p_del

    vj_line = eroded_seqs_dots['v']
    vj_line += ' ' * (germline_j_start - germline_v_end - 2)
    vj_line += eroded_seqs_dots['j']
    vj_line += j_right_extra
    if no_space:
        dot_matches = re.findall('[.][.]*', vj_line)
        assert len(dot_matches) == 1
        vj_line = vj_line.replace(dot_matches[0], color('red', '.no.space.'))

    if len(insertions) != len(d_line) or len(insertions) != len(vj_line):
        print 'ERROR lines unequal lengths in event printer -- insertions %d d %d vj %d' % (len(insertions), len(d_line), len(vj_line)),
        assert no_space
        print ' ...but we\'re out of space so it\'s expected'

    # print insert, d, and vj lines
    if not one_line:
        print '%s    %s   inserts' % (extra_str, insertions)
        print '%s    %s   %s' % (extra_str, d_line, color_gene(line['d_gene']))
        print '%s    %s   %s,%s' % (extra_str, vj_line, color_gene(line['v_gene']), color_gene(line['j_gene']))
    # print query sequence
    print '%s    %s' % (extra_str, final_seq),
    # and then some extra info
    print '   muted: %4.2f' % (float(n_muted) / n_total),
    if 'score' in line:
        print '  score: %s' % line['score'],
    if 'cdr3_length' in line:
        print '   cdr3: %d' % line['cdr3_length'],
    print ''

    line['seq'] = line['seq'].lstrip('.')  # hackey hackey hackey TODO change it
#    assert len(line['seq']) == line['v_5p_del'] + len(hmms['v']) + len(outline['vd_insertion']) + len(hmms['d']) + len(outline['dj_insertion']) + len(hmms['j']) + outline['j_3p_del']

#----------------------------------------------------------------------------------------
def sanitize_name(name):
    """ Replace characters in gene names that make crappy filenames. """
    saniname = name.replace('*', '_star_')
    saniname = saniname.replace('/', '_slash_')
    return saniname

#----------------------------------------------------------------------------------------
def unsanitize_name(name):
    """ Re-replace characters in gene names that make crappy filenames. """
    unsaniname = name.replace('_star_', '*')
    unsaniname = unsaniname.replace('_slash_', '/')
    return unsaniname

#----------------------------------------------------------------------------------------
def read_germlines(data_dir, remove_fp=False, remove_N_nukes=False):
    """ <remove_fp> sometimes j names have a redundant _F or _P appended to their name. Set to True to remove this """
    germlines = {}
    for region in regions:
        germlines[region] = collections.OrderedDict()
        for seq_record in SeqIO.parse(data_dir + '/igh'+region+'.fasta', "fasta"):
            gene_name = seq_record.name
            if remove_fp and region == 'j':
                gene_name = gene_name[:-2]
            seq_str = str(seq_record.seq)
            if remove_N_nukes and 'N' in seq_str:
                seq_str = seq_str.replace('N', 'A')
            germlines[region][gene_name] = seq_str
    return germlines

# ----------------------------------------------------------------------------------------
def get_region(gene_name):
    """ return v, d, or j of gene"""
    assert 'IGH' in gene_name
    region = gene_name[3:4].lower()
    assert region in regions
    return region

# ----------------------------------------------------------------------------------------
def maturity_to_naivety(maturity):
    if maturity == 'memory':
        return 'M'
    elif maturity == 'naive':
        return 'N'
    else:
        assert False

# # ----------------------------------------------------------------------------------------
# def split_gene_name(name):
#     """
#     split name into region, version, allele, etc.
#     e.g. IGHD7-27*01 --> {'region':'d', 'version':7, 'subversion':27, 'allele':1}
#     """
#     return_vals = {}
#     return_vals['region'] = get_region(name)
#     assert name.count('-') == 1
#     return_vals['version'] = name[4 : name.find('-')]
    
#     assert name.count('*') == 1
    

# ----------------------------------------------------------------------------------------
def are_alleles(gene1, gene2):
    """
    Return true if gene1 and gene2 are alleles of the same gene version.
    Assumes they're alleles if everything left of the asterisk is the same, and everything more than two to the right of the asterisk is the same.
    """
    left_str_1 = gene1[0 : gene1.find('*')]
    left_str_2 = gene2[0 : gene1.find('*')]
    right_str_1 = gene1[gene1.find('*')+3 :]
    right_str_2 = gene2[gene1.find('*')+3 :]
    return left_str_1 == left_str_2 and right_str_1 == right_str_2

# ----------------------------------------------------------------------------------------
def are_same_primary_version(gene1, gene2):
    """
    Return true if the bit up to the dash is the same.
    There's probably a real name for that bit.
    """
    str_1 = gene1[0 : gene1.find('-')]
    str_2 = gene2[0 : gene2.find('-')]
    return str_1 == str_2

# ----------------------------------------------------------------------------------------
def read_overall_gene_prob(indir, only_region='', only_gene=''):
    counts = {}
    for region in regions:
        if only_region != '' and region != only_region:
            continue
        counts[region] = {}
        total = 0
        smallest_count = -1  # if we don't find the gene we're looking for, assume it occurs at the lowest rate at which we see any gene
        with opener('r')(indir + '/' + region + '_gene-probs.csv') as infile:  # TODO note this ignores correlations... which I think is actually ok, but it wouldn't hurt to think through it again at some point
            reader = csv.DictReader(infile)
            for line in reader:
                line_count = int(line['count'])
                gene = line[region + '_gene']
                total += line_count
                if line_count < smallest_count or smallest_count == -1:
                    smallest_count = line_count
                if gene not in counts[region]:
                    counts[region][gene] = 0
                counts[region][gene] += line_count
        if only_gene != '' and only_gene not in counts[region]:  # didn't find this gene
            counts[region][only_gene] = smallest_count
        # if region == 'v':
        #     for gene in ['IGHV3-30*12', 'IGHV3-30*07', 'IGHV3-30*03', 'IGHV3-30*10', 'IGHV3-30*11', 'IGHV3-30*06', 'IGHV3-30*19', 'IGHV3-30*17']:  # list of genes for which we don't have info
        #         print gene
        #         assert gene not in counts[get_region(gene)]
        #         counts[get_region(gene)][gene] = smallest_count
        for gene in counts[region]:
            counts[region][gene] /= float(total)
    # print 'return: %d / %d = %f' % (this_count, total, float(this_count) / total)
    if only_gene == '':
        return counts  # oops, now they're probs, not counts. *sigh*
    else:
        return counts[only_region][only_gene]

# ----------------------------------------------------------------------------------------
def hamming(seq1, seq2):
    assert len(seq1) == len(seq2)
    total = 0
    for ch1,ch2 in zip(seq1,seq2):
        if ch1 != ch2:
            total += 1
    return total

# ----------------------------------------------------------------------------------------
def get_key(query_name, second_query_name):
    """
    Return a hashable combination of the two query names that's the same if we reverse their order.
    At the moment, just add 'em up.
    """
    # assert query_name != ''
    # if second_query_name == '':
    #     second_query_name = '0'
    # return int(query_name) + int(second_query_name)
    assert query_name != ''
    if second_query_name == '':
        second_query_name = '0'
    return '.'.join(sorted([query_name, second_query_name]))

# ----------------------------------------------------------------------------------------
def prep_dir(dirname, wildling=None, multilings=None):
    """ make <dirname> if it d.n.e., and if shell glob <wildling> is specified, remove existing files which are thereby matched """
    if os.path.exists(dirname):
        if wildling != None:
            for fname in glob.glob(dirname + '/' + wildling):
                os.remove(fname)
        if multilings != None:  # allow multiple file name suffixes
            for wild in multilings:
                for fname in glob.glob(dirname + '/' + wild):
                    os.remove(fname)
    else:
        os.makedirs(dirname)
    if len([fname for fname in os.listdir(dirname) if os.path.isfile(dirname + '/' + fname)]) != 0:  # make sure there's no other files in the dir
        print 'ERROR files remain in',dirname,'despite wildling',
        if wildling != None:
            print wildling
        if multilings != None:
            print multilings
        assert False

# ----------------------------------------------------------------------------------------
def fraction_uncertainty(obs, total):
    """ Return uncertainty on the ratio n / total """
    assert obs <= total
    if total == 0.0:
        return 0.0
    lo = beta.ppf(1./6, 1 + obs, 1 + total - obs)
    hi = beta.ppf(1. - 1./6, 1 + obs, 1 + total - obs)
    if float(obs) / total < lo:  # if k/n very small (probably zero), take a one-sided c.i. with 2/3 the mass
        lo = 0.
        hi = beta.ppf(2./3, 1 + obs, 1 + total - obs)
    if float(obs) / total > hi:  # same deal if k/n very large (probably one)
        lo = beta.ppf(1./3, 1 + obs, 1 + total - obs)
        hi = 1.
    return (lo,hi)