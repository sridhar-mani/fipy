#!/bin/bash

# E.g.,
# bash examples/benchmarking/solvers/dispatch.sh --env fipy27 --solversuite pysparse --log examples/benchmarking/solvers/macos_config.json diffusion.py --preconditioner=ilu

USAGE="usage: $0 [-h] [--env ENV] [--cmd CMD] [--np NP] [--mprof] [--] SCRIPT [ARGS]

Iterates over solvers and mesh sizes by calling setup.sh, which activates
the appropriate conda environment and calls python on SCRIPT

positional arguments:
  SCRIPT      Python script to launch (expected to be in same
              directory as $0)

optional arguments:
  -h, --help  show this help message and exit
  --qsub      Invoke SCRIPT using 'qsub -cwd' for Sun grid engine
              (default: invoke using bash)
  --sbatch    Invoke SCRIPT using 'sbatch ???' for slurm
              (default: invoke using bash)
  --env ENV   Conda environment to activate before invoking SCRIPT
              (default: fipy)
  --np NP     Number of processes to invoke SCRIPT with (default: 1)
  --mprof     Whether to run mprof profiler (default: False)
  --log CONFIG LOG  Path to log configuration file template and
                    path for log file.
  --solversuite SUITE   Solver package to use
  --powermin POWERMIN   Power of ten for minimum size, minsize = 10**POWERMIN
  --powermin POWERMAX   Power of ten for maximum size, maxsize = 10**POWERMAX
  --powerstep POWERSTEP Increment in power of ten for size"

QSUB=0
SBATCH=""
ENV=fipy
NP=1
LOGCONFIG=""
LOGFILE=""
PYTHON=python
SOLVERSUITE=petsc
PRECONDITIONER=none
POWERMIN=1
POWERMAX=6
POWERSTEP=1

while [[ $# > 0 ]] && [[ $1 == -* ]]
do
    case "$1" in
        --qsub)
            QSUB=1
            ;;
        --sbatch)
            SBATCH="$2"
            shift # option has parameter
            ;;
        --env)
            ENV="$2"
            shift # option has parameter
            ;;
        --np)
            NP="$2"
            shift # option has parameter
            ;;
        --log)
            LOGCONFIG="$2"
            LOGFILE="$3"
            shift # option has two parameters
            shift
            ;;
        --mprof)
            PYTHON="mprof run"
            ;;
        --solversuite)
            SOLVERSUITE="$2"
            shift # option has parameter
            ;;
        --powermin)
            POWERMIN="$2"
            shift # option has parameter
            ;;
        --powermax)
            POWERMAX="$2"
            shift # option has parameter
            ;;
        --powerstep)
            POWERMAX="$2"
            shift # option has parameter
            ;;
        -h|--help)
            echo "$USAGE"
            exit 0
            ;;
        --)
            # end of options
            shift
            break
            ;;
        -*)
            # unknown option
            echo Unknown option: $1>&2
            exit 10
            ;;
    esac
    shift # option(s) fully processed, proceed to next input argument
done

if [[ "$#" < 1 ]]; then
    echo "$USAGE"
    exit 1
fi

SCRIPT=$1
shift

if [[ $NP > 1 ]]; then
    MPI="mpirun -np ${NP}"
else
    MPI=""
fi

for (( POWER=${POWERMIN}; POWER<=${POWERMAX}; POWER+=${POWERSTEP} ))
do
    size=$((10**${POWER}))
    for solver in pcg cgs gmres lu
    do
        INVOCATION="OMP_NUM_THREADS=1 FIPY_SOLVERS=${SOLVERSUITE} ${LOG_CONFIG} \
          ${MPI} ${PYTHON} ${BASH_SOURCE%/*}/${SCRIPT} \
          --numberOfElements=${size} --solver=${solver} $@"

        JOBNAME="${SCRIPT}-${size}-${solver}"

        if [[ $QSUB == 1 ]]; then
            qsub -cwd -pe nodal ${NP} -q "wide64" -o "${dir}" -e "${dir}" "${BASH_SOURCE%/*}/setup.sh" --env "${ENV}" -- ${INVOCATION}
        elif [[ -n $SBATCH ]]; then
            sbatch --partition=${SBATCH} --job-name=${JOBNAME} --ntasks=${NP} --ntasks-per-core=2 \
              "${BASH_SOURCE%/*}/setup.sh" --log ${LOGCONFIG} ${LOGFILE} --env "${ENV}" -- ${INVOCATION}
        else
            echo bash "${BASH_SOURCE%/*}/setup.sh" --env "${ENV}" -- ${INVOCATION}
            bash "${BASH_SOURCE%/*}/setup.sh" --log ${LOGCONFIG} ${LOGFILE} --env "${ENV}" -- ${INVOCATION}
        fi
    done
done
