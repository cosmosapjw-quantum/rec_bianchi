#!/usr/bin/env bash
set -euo pipefail
mkdir -p "$1"
base="https://zenodo.org/api/records/21165907/files"
curl --fail --location --retry 2 --connect-timeout 15 --max-time 120 "$base/hd_population_grids.fits/content" -o "$1/hd_population_grids.fits"
curl --fail --location --retry 2 --connect-timeout 15 --max-time 120 "$base/hd_population_grids_altex.fits/content" -o "$1/hd_population_grids_altex.fits"
curl --fail --location --retry 2 --connect-timeout 15 --max-time 120 "$base/hd_lamda.dat/content" -o "$1/hd_lamda.dat"
curl --fail --location --retry 2 --connect-timeout 15 --max-time 120 "$base/hd_lamda_altex.dat/content" -o "$1/hd_lamda_altex.dat"
(cd "$1" && printf '%s  %s\n' \
  '3fffb1591b0f96b254210ed54599667a' 'hd_population_grids.fits' \
  '012ff8819227cd9888f92a7aedafb3f2' 'hd_population_grids_altex.fits' \
  'c45c4740011df579a973a7c336c5bc22' 'hd_lamda.dat' \
  '1f0275f383786c890bfbb0c83bb4f74b' 'hd_lamda_altex.dat' > ORIGINAL_MD5SUMS && md5sum --check ORIGINAL_MD5SUMS && sha256sum *.fits *.dat > ORIGINAL_SHA256SUMS)
