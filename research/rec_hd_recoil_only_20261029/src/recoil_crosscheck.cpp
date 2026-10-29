#include <array>
#include <cmath>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <limits>
// Independent bounded C++20 long-double check on eight source-derived public pairs.
// The original LAMDA/CDMS bytes are not included or authenticated here.
int main(){
constexpr long double h=6.62607015e-34L,c=299792458.0L,u=1.66053906660e-27L;
constexpr std::array<long double,8> nu={
  13374930469958794919.0L/5000000.0L,1332890250930289919.0L/250000.0L,
  19879323162796857291.0L/2500000.0L,52591535167862954543.0L/5000000.0L,
  13015354732561910729.0L/1000000.0L,38571409466318598107.0L/2500000.0L,
  22182121643381812819.0L/1250000.0L,49892404686912474057.0L/2500000.0L};
constexpr std::array<long double,8> d={-41205081.0L/5000000.0L,
  -236919710081.0L/250000.0L, 2710796857291.0L/2500000.0L,
  -238137045457.0L/5000000.0L,1245461910729.0L/1000000.0L,
  -4568931401893.0L/2500000.0L,1764006812819.0L/1250000.0L,
  17162474057.0L/2500000.0L};
std::cout<<std::setprecision(19);
int excluded=0,gatefail=0;
for(int k=0;k<8;++k){
  const long double upper = (h*nu[k]*nu[k])/(4*u*c*c);
  const long double reference=(h*nu[k]*nu[k])/(6*u*c*c);
  const bool mismatch=std::abs(d[k])>upper;
  const bool gate=std::abs(d[k])>35.0L;
  if(k>0 && mismatch)++excluded;
  if(gate)++gatefail;
  if(!(reference>0.0L && upper>reference && mismatch))return 4;
  std::cout << (k+1) << " " << upper << " " << reference << " " << d[k] << '\n';
}
if(excluded!=7 || gatefail!=7)return 5;
std::cerr<<"CPP_PASS: 8/8 source-shape rows; seven high J exceed recoil bound; 35Hz FAIL7/8\n";
return 0;
}
