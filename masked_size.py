#! /usr/bin/env python
# -*- coding: utf-8 -*-

import pyfaidx
from collections import Counter
import sys
import re
from ancestor import Ancestor


def main():
    """
    usage: python masked_size.py -h
    """
    import argparse

    parser = argparse.ArgumentParser(description='print masked chromosome '
                                                 'size')
    parser.add_argument('anc_fasta_file', type=str, default=None,
                        help='path to ancestral alignment fasta (one '
                             'chromosome)')
    parser.add_argument('--mask_file', type=str, default=sys.stdin,
                        help='path to bed file mask (default stdin)')
    parser.add_argument('--k', type=int, default=3,
                        help='kmer context')
    parser.add_argument('--target', type=int, default=None,
                        help='0-based mutation target position in kmer (default middle)')
    parser.add_argument('--sep', type=str, default=':',
                        help='field delimiter in fasta headers (default ":")')
    parser.add_argument('--chrom_pos', type=int, default=2,
                        help='0-based chromosome field position in fasta headers (default 2)')
    parser.add_argument('--strand_file', type=str, default=None,
                        help='path to bed file with regions where reverse '
                             'strand defines mutation context, e.g. direction '
                             'of replication or transcription (default collapse '
                             'reverse complements)')
    args = parser.parse_args()

    ancestor = Ancestor(args.anc_fasta_file, args.k, args.target, args.strand_file)

    # parse chromosome names from fasta headers
    chrom_map = {name.split(args.sep)[args.chrom_pos]:
                 name for name in ancestor.fasta.keys()}

    if args.mask_file is not sys.stdin:
        args.mask_file = open(args.mask_file, 'r')

    sizes = Counter()
    for line in args.mask_file:
        chrom, start, end = line.rstrip().split('\t')
        context_gen = (ancestor.stranded_context(chrom_map[chrom], pos)
                       for pos in range(int(start), int(end)))
        sizes.update(context for context in context_gen if context is not None)

    for kmer in sorted(sizes):
        # print if unambiguous
        if re.match('^[ACGT]+$', kmer):
            print(f'{kmer}\t{sizes[kmer]}')


if __name__ == '__main__':
    main()
