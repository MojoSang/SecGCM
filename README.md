This is the source code of paper "SecGCM: Secure Group Closeness Maximization on Graphs with Secure Multi-party Computation".

# Experiment Setup

Our experiments are conducted on a desktop equipped with Intel (R) Core i7-11700K CPU @ 3.60GHz×4 running Ubuntu 20.04 on VMware Workstation allocated with 48 GB memory.

# Compile & Run

## Input

The input data should be stored in `./mp-spdz-0.3.8/mp-spdz-0.3.8/Player-Data`.

The Graph database can be found in [NetworkRepository](https://networkrepository.com/)

## Compile

```
cd ./mp-spdz-0.3.8/mp-spdz-0.3.8
./Script/Setup-ssl.sh 3
./Compile.py -R 64 secesto
```

## Run

```
./Script/ring.sh secesto
```

