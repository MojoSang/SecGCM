This is the source code of paper "SecGCM: Secure Group Centrality Maximization on Graphs with Secure Multi-party Computation".

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
## Three-Party Computation Setup (Using Virtual Machines)

This project supports secure multi-party computation (MPC) using three virtual machines to simulate three parties.


1. **Select One VM as the Host:**

   Run the following command on the host VM:

   ```bash
   ./Script/ring.sh -h localhost -p 0 -N 2 secesto
   ```

2. **Connect the Other Two VMs:**

   Run the following commands on the other two VMs (replace `xxx.xxx.xxx.xxx` with the host VM's IP address):

   ```bash
   ./Script/ring.sh -h xxx.xxx.xxx.xxx -p 1 -N 2 secesto
   ./Script/ring.sh -h xxx.xxx.xxx.xxx -p 2 -N 2 secesto
   ```

### Important Note

> All source files must be compiled locally on each machine before running the computation.

---

