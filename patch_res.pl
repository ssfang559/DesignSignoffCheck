#!/bin/env perl

=head1 NAME

patch_res_values - Script to patch in resistor subcircuits and values into a CDL/Spice netlist whose resistors do not have resistance properties

=head1 SYNOPSIS

    --process, -p   Name of the runset process, which can be found in the path /apps/imctf/runset/calibre/<process>. For example: imc19n_TX (required)
    --input, -i     Name and path of the input CDL/Spice netlist (required)
    --output, -o    Name and path of the output CDL/Spice netlist (required)

=head1 VERSION

1.0

=head1 AUTHOR

Wen Sun, Wu (wensun.wu@cxmt.com)

=cut

#----------------------------------------------------------------------------------#

use strict;
use warnings;
use Getopt::Long qw(HelpMessage);

# Global hash to store sheet resistances for various resistor models in each supported process
our %sheetres_hash = (
    'imc19n_RW' => {
        'rm0_2t_ckt' => 4.34,
        'rm1_2t_ckt' => 0.10,
        'rm2_2t_ckt' => 0.09,
        'rm3_2t_ckt' => 0.07,
        'rndiff_2t_ckt' => 139.93,
        'rnldd3_2t_ckt' => 1839.33,
        'rnpo_2t_ckt' => 12.11,
        'rpdiff_2t_ckt' => 231.93,
        'brknet' => 0.001,
    },
    'imc17n_PS' => {
        'rm0_2t_ckt' => 15,
        'rm1_2t_ckt' => 0.19,
        'rm2_2t_ckt' => 0.11,
        'rm3_2t_ckt' => 0.11,
        'rndiff_2t_ckt' => 227,
        'rnpo_2t_ckt' => 5,
        'brknet' => 0.001,
    },
    'cxmt10G3' => {
        'rm0_2t_ckt' => 12,
        'rm1_2t_ckt' => 0.14,
        'rm2_2t_ckt' => 0.11,
        'rm3_2t_ckt' => 0.11,
        'rm4_2t_ckt' => 0.0625,
        'rndiff_2t_ckt' => 227,
        'rndiff_3t_ckt' => 227,
        'rnpo_2t_ckt' => 5,
        'brknet' => 0.001,
    },
    'cxmt10G4' => {
        'rm0_2t_ckt' => 15,
        'rm1_2t_ckt' => 0.28,
        'rm2_2t_ckt' => 0.15,
        'rm3_2t_ckt' => 0.15,
        'rm4_2t_ckt' => 0.055,
        'rndiff_3t_ckt' => 223,
        'rnpo_2t_ckt' => 4.9,
        'brknet' => 0.001,
    },
    'cxmt10G5' => {
        'rm0_2t_ckt' => 12.5,
        'rm1_2t_ckt' => 0.27,
        'rm2_2t_ckt' => 0.19,
        'rm3_2t_ckt' => 0.19,
        'rm4_2t_ckt' => 0.087,
        'rndiff_2t_ckt' => 390,
        'rnpo_2t_ckt' => 12.5,
        'brknet' => 0.001,
    },
    'cxmt10G5plus' => {
        'rm0_2t_ckt' => 12.5,
        'rm1_2t_ckt' => 0.36,
        'rm2_2t_ckt' => 0.18,
        'rm3_2t_ckt' => 0.18,
        'rm4_2t_ckt' => 0.18,
        'rm5_2t_ckt' => 0.055,
        'rndiff_3t_ckt' => 390,
        'rnpo_2t_ckt' => 12.5,
        'brknet' => 0.001,
    },
    'cxmt10G6' => {
        'rm0_2t_ckt' => 12.5,
        'rm1_2t_ckt' => 0.36,
        'rm2_2t_ckt' => 0.18,
        'rm3_2t_ckt' => 0.18,
        'rm4_2t_ckt' => 0.18,
        'rm5_2t_ckt' => 0.055,
        'rndiff_3t_ckt' => 390,
        'rnpo_2t_ckt' => 12.5,
        'brknet' => 0.001,
    },
);

##########################################################
# Read the input netlist and generate the output netlist #
##########################################################
sub gen_out_netlist {
    my $hashref = shift;
    my $process = ${$hashref->{process}};
    my $infile = ${$hashref->{infile}};
    my $outfile = ${$hashref->{outfile}};
    my $currshres;
    my $randomnum = time();
    my %model2num = ();
    # Create the output netlist with all the relevant resistor subcircuits to be injected
  if($process eq "cxmt10G3" || "cxmt10G4" || "cxmt10G5plus" || "cxmt10G6") {
    open(my $ofh, ">", $outfile) or die("Error: Failed to open file $outfile for writing!: $!");
    foreach my $resmodel (keys(%{$sheetres_hash{$process}})) {
        $model2num{$resmodel} = "res_${randomnum}";
        $currshres = $sheetres_hash{$process}{$resmodel};
        if($resmodel eq "brknet" && $process eq "cxmt10G4") {
            # brknet don't need to handle in cxmt10G4
            next;
        }
        elsif($resmodel eq "brknet" && $process ne "cxmt10G4"){
            # Special handling is needed for this particular device
            print $ofh ".SUBCKT $model2num{$resmodel} netP netN\n";
            print $ofh "RR0 netP netN $resmodel ${currshres}\n";
        }
        elsif($resmodel eq "rndiff_3t_ckt") {
            # Assume that in the LVS rule deck, the w and l properties are in lowercase, and that the calling statement in the Spice netlist has defined W and L in the uppercase
            print $ofh ".SUBCKT $model2num{$resmodel} netP netN SUB\n";
            print $ofh "RR0 netP netN $resmodel R=${currshres}*L/W w=W l=L \$SUB=SUB\n";
        }
        else {
            # Assume that in the LVS rule deck, the w and l properties are in lowercase, and that the calling statement in the Spice netlist has defined W and L in the uppercase
            print $ofh ".SUBCKT $model2num{$resmodel} netP netN\n";
            print $ofh "RR0 netP netN $resmodel ${currshres}*L/W w=W l=L\n";
        }
        print $ofh ".ENDS\n\n";
        $randomnum++;
    }
    # Now read the input netlist
    open(my $ifh, "<", $infile) or die("Error: Failed to open $infile for reading!: $!");
    while(my $inline = <$ifh>) {
        if($inline =~ /^\s*(R\S+)\s+(\S+)\s+(\S+)\s+(?|\[?([^ \]]+)\]?\s+((?:W|L)\S+)\s+((?:W|L)\S+)\s*$)/) {
            if(defined($model2num{$4})) {
                if(defined($6)) {
                    print $ofh "X$1 $2 $3 / $model2num{$4} $5 $6\n";
                } else {
                    print $ofh "X$1 $2 $3 / $model2num{$4} $5\n";
                }
            } else {
                die "Error: Resistor $4 not mapped to a random subcircuit name!\n";
            }
        }
        elsif($inline =~ /^\s*(R\S+)\s+(\S+)\s+(\S+)\s+\$SUB=(\S+)\s+(?|\[?([^ \]]+)\]?\s+((?:W|L)\S+)\s+((?:W|L)\S+)\s*$)/) {
            if(defined($model2num{$5})) {
                if(defined($7)) {
                    print $ofh "X$1 $2 $3 $4 / $model2num{$5} $6 $7\n";
                } else {
                    print $ofh "X$1 $2 $3 / $model2num{$5} $6\n";
                }
            } else {
                die "Error: Resistor $5 not mapped to a random subcircuit name!\n";
            }
        }
        elsif($inline =~ /^(.SUBCKT\s+brknet\s+MINUS\s+PLUS\s+lay=)WL\s*$/) {
            print $ofh "$1\"WL\"\n";
        }
        elsif($inline =~ /^\s*(R\S+)\s+(\S+)\s+(\S+)\s+(?|\$\[?([^ \]]+)\]?\s+\$((?:W|L)\S+)\s+\$((?:W|L)\S+)\s*$|(brknet)\s+(lay\S+)\s*$)/) {
            if(defined($model2num{$4})) {
                if(defined($6)) {
                    print $ofh "X$1 $2 $3 / $model2num{$4} $5 $6\n";
                } else {
                    print $ofh "X$1 $2 $3 / $model2num{$4} $5\n";
                }
            } else {
                die "Error: Resistor $4 not mapped to a random subcircuit name!\n";
            }
        }
        elsif($inline =~ /^\s*(R\S+)\s+(\S+)\s+(\S+)\s+\$SUB=(\S+)\s+(\S+)\s+(w\S+)\s+(l\S+)\s+(flag_res\S+)\s+(nm\S+)\s*$/)
        {
            print $ofh "X$1 $2 $3 $4 / $model2num{$5} $6 $7 $8 $9\n"
        }
         elsif($inline =~ /^\s*(R\S+)\s+(\S+)\s+(\S+)\s+\$SUB=(\S+)\s+(\S+)\s+(w\S+)\s+(l\S+)\s+(flag_res\S+)\s*$/)
        {
            print $ofh "X$1 $2 $3 $4 / $model2num{$5} $6 $7 $8\n"
        }
        else {
            print $ofh $inline;
        }
    }
    close($ifh);
    close($ofh);
  }
  else {
    open(my $ofh, ">", $outfile) or die("Error: Failed to open file $outfile for writing!: $!");
    foreach my $resmodel (keys(%{$sheetres_hash{$process}})) {
        $model2num{$resmodel} = "res_${randomnum}";
        $currshres = $sheetres_hash{$process}{$resmodel};
        print $ofh ".SUBCKT $model2num{$resmodel} netP netN\n";
        if($resmodel eq "brknet") {
            # Special handling is needed for this particular device
            print $ofh "RR0 netP netN $resmodel ${currshres}\n";
        } else {
            # Assume that in the LVS rule deck, the w and l properties are in lowercase, and that the calling statement in the Spice netlist has defined W and L in the uppercase
            print $ofh "RR0 netP netN $resmodel ${currshres}*L/W w=W l=L\n";
        }
        print $ofh ".ENDS\n\n";
        $randomnum++;
    }
    # Now read the input netlist
    open(my $ifh, "<", $infile) or die("Error: Failed to open $infile for reading!: $!");
    while(my $inline = <$ifh>) {
        if($inline =~ /^\s*(R\S+)\s+(\S+)\s+(\S+)\s+(?|\$\[?([^ \]]+)\]?\s+\$((?:W|L)\S+)\s+\$((?:W|L)\S+)\s*$|(brknet)\s+(lay\S+)\s*$)/) {
            if(defined($model2num{$4})) {
                if(defined($6)) {
                    print $ofh "X$1 $2 $3 / $model2num{$4} $5 $6\n";
                } else {
                    print $ofh "X$1 $2 $3 / $model2num{$4} $5\n";
                }
            } else {
                die "Error: Resistor $4 not mapped to a random subcircuit name!\n";
            }
        } else {
            print $ofh $inline;
        }
    }
    close($ifh);
    close($ofh);
  }
}

#######################################
# Simple command-line argument parser #
#######################################
sub parse_args {
    my($process, $infile, $outfile);
    my $helpmessage = "\npatch_res_values - Script to patch in resistor subcircuits and values into a CDL/Spice netlist whose resistors do not have resistance properties\n";
    GetOptions(
        "process=s"     => \$process,
        "infile=s"      => \$infile,
        "outfile=s"     => \$outfile,
        "help"          => sub {HelpMessage("-msg" => $helpmessage, "-exitval" => 0)},
    ) or HelpMessage("-msg" => $helpmessage, "-exitval" => 1);

    # Enforce mandatory parameters
    HelpMessage("-msg" => $helpmessage, "-exitval" => 1) unless($process and $infile and $outfile);

    # Organise the parameters into a hash
    my %args = (
        "process"   => \$process,
        "infile"    => \$infile,
        "outfile"   => \$outfile,
    );
    return \%args;
}

###############################################
# Main subroutine to control the program flow #
###############################################
sub main {
    # Parse command-line arguments
    my $refargs = parse_args();
    # Read the input netlist and generate the output netlist
    gen_out_netlist($refargs);
}

main();
