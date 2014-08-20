ssd-cache
=========


Works only with Ubuntu 13.10 or higher with linux 3.10 or higher.


sundarcs@nimbnode19:~|⇒  uname -a
Linux nimbnode19 3.13.0-32-generic #57-Ubuntu SMP Tue Jul 15 03:51:08 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux

```
sundarcs@nimbnode19:~|⇒  sudo lsblk
NAME                         MAJ:MIN RM   SIZE RO TYPE MOUNTPOINT
sda                            8:0    0 465.8G  0 disk
├─sda1                         8:1    0   4.7G  0 part /boot
├─sda2                         8:2    0     1K  0 part
└─sda5                         8:5    0 461.1G  0 part
  ├─nimbnode19-root (dm-0)   252:0    0 345.1G  0 lvm  /
  ├─nimbnode19-swap_1 (dm-1) 252:1    0    16G  0 lvm  [SWAP]
  └─nimbnode19-iotest (dm-2) 252:2    0    80G  0 lvm
sdb                            8:16   0 186.3G  0 disk     **SSD**
sdc                            8:32   0 186.3G  0 disk     **SSD**
sdd                            8:48   0 465.8G  0 disk     **HDD**
sde                            8:64   0 465.8G  0 disk     **HDD**
sdf                            8:80   0 465.8G  0 disk     **HDD**
```

```
sundarcs@nimbnode19:~|⇒  sudo gparted 2> /dev/null
======================
libparted : 2.3
======================
```

***
Create sdc1(the SSD), sdd1(1st HDD), sde1(2nd HDD) with ext4. We will wipe sdc1’s filestsyem in the forth coming steps but it is necessary to create that partition first or else it throws an "wipefs: WARNING: /dev/sd*: appears to contain 'dos' partition table” error.
***


sundarcs@nimbnode19:~|⇒  sudo wipefs -a /dev/sdc1
2 bytes were erased at offset 0x438 (ext4)
they were: 53 ef

sundarcs@nimbnode19:~|⇒  sudo wipefs -a /dev/sdd1
2 bytes were erased at offset 0x438 (ext4)
they were: 53 ef
sundarcs@nimbnode19:~|⇒  sudo wipefs -a /dev/sde1
2 bytes were erased at offset 0x438 (ext4)
they were: 53 ef

```
sundarcs@nimbnode19:~|⇒  sudo make-bcache -C /dev/sdc1
UUID:                   0d0eed81-319f-46c9-99e4-498d21bf5af5
Set UUID:               d55cb762-68fe-4553-9dd7-022e77065af9 (This will be the UUID that you will be attaching to as many hard disks as you are trying to cache. You will NOT be attaching the hdd UUID's)
version:                0
nbuckets:               381562
block_size:             1
bucket_size:            1024
nr_in_set:              1
nr_this_dev:            0
first_bucket:           1

sundarcs@nimbnode19:~|⇒  sudo make-bcache -B /dev/sdd1
UUID:                   1effa1f4-1538-49cf-8bec-2082d391cdb1
Set UUID:               6d7e4b06-ba85-45d3-8f5f-ada6e91cba97 (You will never use this. Ever.)
version:                1
block_size:             1
data_offset:            16

sundarcs@nimbnode19:~|⇒  sudo make-bcache -B /dev/sde1
UUID:                   bf70ee52-3891-4663-93fe-f64beafc014c
Set UUID:               b17796db-59f3-491f-baac-119325c69cb7 (You will not use this either)
version:                1
block_size:             1
data_offset:            16
```

sundarcs@nimbnode19:~|⇒  sudo su
root@nimbnode19:/home/sundarcs# echo d55cb762-68fe-4553-9dd7-022e77065af9 > /s
ys/block/bcache0/bcache/attach
root@nimbnode19:/home/sundarcs# echo d55cb762-68fe-4553-9dd7-022e77065af9 > /sys/block/bcache1/bcache/attach
root@nimbnode19:/home/sundarcs# mkfs.ext4 /dev/bcache0
mke2fs 1.42.9 (4-Feb-2014)
Discarding device blocks: done
Filesystem label=
OS type: Linux
Block size=4096 (log=2)
Fragment size=4096 (log=2)
Stride=0 blocks, Stripe width=0 blocks
30531584 inodes, 122096382 blocks
6104819 blocks (5.00%) reserved for the super user
First data block=0
Maximum filesystem blocks=4294967296
3727 block groups
32768 blocks per group, 32768 fragments per group
8192 inodes per group
Superblock backups stored on blocks:
        32768, 98304, 163840, 229376, 294912, 819200, 884736, 1605632, 2654208,
        4096000, 7962624, 11239424, 20480000, 23887872, 71663616, 78675968,
        102400000

Allocating group tables: done
Writing inode tables: done
Creating journal (32768 blocks): done
Writing superblocks and filesystem accounting information: done

Writing superblocks and filesystem accounting information: done

root@nimbnode19:/home/sundarcs# mkfs.ext4 /dev/bcache1
mke2fs 1.42.9 (4-Feb-2014)
Discarding device blocks: done
Filesystem label=
OS type: Linux
Block size=4096 (log=2)
Fragment size=4096 (log=2)
Stride=0 blocks, Stripe width=0 blocks
30531584 inodes, 122096382 blocks
6104819 blocks (5.00%) reserved for the super user
First data block=0
Maximum filesystem blocks=4294967296
3727 block groups
32768 blocks per group, 32768 fragments per group
8192 inodes per group
Superblock backups stored on blocks:
        32768, 98304, 163840, 229376, 294912, 819200, 884736, 1605632, 2654208,
        4096000, 7962624, 11239424, 20480000, 23887872, 71663616, 78675968,
        102400000

Allocating group tables: done
Writing inode tables: done
Creating journal (32768 blocks): done
Writing superblocks and filesystem accounting information: done

root@nimbnode19:/home/sundarcs# mount /dev/bcache0 /mnt/hdd1/
root@nimbnode19:/home/sundarcs# mount /dev/bcache1 /mnt/hdd2/

```
sundarcs@nimbnode19:~|⇒  sudo lsblk
NAME                         MAJ:MIN RM   SIZE RO TYPE MOUNTPOINT
sda                            8:0    0 465.8G  0 disk
├─sda1                         8:1    0   4.7G  0 part /boot
├─sda2                         8:2    0     1K  0 part
└─sda5                         8:5    0 461.1G  0 part
  ├─nimbnode19-root (dm-0)   252:0    0 345.1G  0 lvm  /
  ├─nimbnode19-swap_1 (dm-1) 252:1    0    16G  0 lvm  [SWAP]
  └─nimbnode19-iotest (dm-2) 252:2    0    80G  0 lvm
sdb                            8:16   0 186.3G  0 disk
sdc                            8:32   0 186.3G  0 disk
└─sdc1                         8:33   0 186.3G  0 part
  ├─bcache0                  251:0    0 465.8G  0 disk /mnt/hdd1
  └─bcache1                  251:1    0 465.8G  0 disk /mnt/hdd2
sdd                            8:48   0 465.8G  0 disk
└─sdd1                         8:49   0 465.8G  0 part
  └─bcache0                  251:0    0 465.8G  0 disk /mnt/hdd1
sde                            8:64   0 465.8G  0 disk
└─sde1                         8:65   0 465.8G  0 part
  └─bcache1                  251:1    0 465.8G  0 disk /mnt/hdd2
sdf                            8:80   0 465.8G  0 disk
```