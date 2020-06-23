#!/usr/bin/env python3

import argparse
import sys

try:
    from pycgtool.pycgtool import main, map_only
    from pycgtool.interface import Options
    from pycgtool.functionalforms import FunctionalForms
except SyntaxError:
    raise RuntimeError("PyCGTOOL requires Python 3.2 or greater")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Perform coarse-grain mapping of atomistic trajectory")
    input_files = parser.add_argument_group("Input files")
    input_files.add_argument('-g', '--gro', type=str, required=True, help="GROMACS GRO file")
    input_files.add_argument('-m', '--map', type=str, help="Mapping file")
    input_files.add_argument('-x', '--xtc', type=str, help="GROMACS XTC file")
    input_files.add_argument('-b', '--bnd', type=str, help="Bonds file")
    input_files.add_argument('-i', '--itp', type=str, help="GROMACS ITP file")

    parser.add_argument('--advanced', default=False, action='store_true', help="Show advanced options menu")
    parser.add_argument('--outputxtc', default=False, action='store_true', help="Output a pseudo-CG trajectory")
    parser.add_argument('--quiet', default=False, action='store_true', help="Hide progress bars")
    input_files.add_argument('--begin', type=int, default=0, help="Frame number to begin")
    input_files.add_argument('--end', type=int, default=-1, help="Frame number to end")

    advanced = parser.add_argument_group("Advanced configuration")
    advanced.add_argument("--output_name", help="Base name of output files", default="out", type=str, metavar="STRING")
    advanced.add_argument("--output", help="Coordinate output format", default="gro", type=str, metavar="STRING")
    advanced.add_argument("--map-only", help="Run in mapping-only mode", default=None, metavar="BOOL")
    advanced.add_argument("--map-center", help="Mapping method", default="geom", choices=["geom", "mass"], metavar="{geom|mass}")
    advanced.add_argument("--constr-threshold", help="Convert stiff bonds to constraints over", default=100000.0, type=float, metavar="FLOAT")
    advanced.add_argument("--dump-measurements", help="Whether to output bond measurements", default=None, metavar="BOOL")
    advanced.add_argument("--dump-n-values", help="How many measurements to output", default=10000, type=int, metavar="INT")
    advanced.add_argument("--output-forcefield", help="Output a GROMACS forcefield directory?", default=False, type=bool, metavar="BOOL")
    advanced.add_argument("--temperature", help="Temperature of reference simulation", default=310.0, type=float, metavar="FLOAT")
    advanced.add_argument("--default-fc", help="Use default MARTINI force constants?", default=False, type=bool, metavar="BOOL")
    advanced.add_argument("--generate-angles", help="Generate angles from bonds", default=False, type=bool, metavar="BOOL")
    advanced.add_argument("--generate-dihedrals", help="Generate dihedrals from bonds", default=False, type=bool, metavar="BOOL")

    func_forms = FunctionalForms()

    args = parser.parse_args()
    config = Options([
        ("output_name", args.output_name),
        ("output", args.output),
        ("output_xtc", args.outputxtc),
        ("map_only", args.map_only or (args.map_only is None and not bool(args.bnd))),
        ("map_center", args.map_center),
        ("constr_threshold", args.constr_threshold),
        ("dump_measurements", args.dump_measurements or (args.dump_measurements is None and bool(args.bnd) and not bool(args.map))),
        ("dump_n_values", args.dump_n_values),
        ("output_forcefield", args.output_forcefield),
        ("temperature", args.temperature),
        ("default_fc", args.default_fc),
        ("generate_angles", args.generate_angles),
        ("generate_dihedrals", args.generate_dihedrals),
        ("length_form", "harmonic"),
        ("angle_form", "cosharmonic"),
        ("dihedral_form", "harmonic")
    ], args)

    if not args.map and not args.bnd:
        parser.error("One or both of -m and -b is required.")

    if args.advanced:
        try:
            config.interactive()
        except KeyboardInterrupt:
            sys.exit(0)
    else:
        print("Using GRO: {0}".format(args.gro))
        print("Using XTC: {0}".format(args.xtc))

    if config.map_only:
        map_only(args, config)
    else:
        main(args, config)
