ClearAll["Global`*"];

pi = {p1,p2,p3};
ki = {ki1,ki2,ki3};
kf = {kf1,kf2,kf3};
pf = pi + hb (ki-kf);

energyRule =
  EB -> EA + (pi.pi-pf.pf)/(2 M) + hb (wi-wf);

DabsF =
  EI-EA + ((pi+hb ki).(pi+hb ki)-pi.pi)/(2 M)-hb wi;
DemF =
  EI-EA + ((pi-hb kf).(pi-hb kf)-pi.pi)/(2 M)+hb wf;

DabsR =
  EI-EB + ((-pf-hb kf).(-pf-hb kf)-pf.pf)/(2 M)-hb wf;
DemR =
  EI-EB + ((-pf+hb ki).(-pf+hb ki)-pf.pf)/(2 M)+hb wi;

FullSimplify[(DabsR /. energyRule)-DabsF]
FullSimplify[(DemR /. energyRule)-DemF]

internalRule = EB -> EA + hb (wi-wf);
FullSimplify[
  {
    EI-EB-hb wf-(EI-EA-hb wi),
    EI-EB+hb wi-(EI-EA+hb wf)
  } /. internalRule
]
