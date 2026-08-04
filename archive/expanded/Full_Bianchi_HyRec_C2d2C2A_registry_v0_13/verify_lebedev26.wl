ClearAll["Global`*"];

axes = Flatten[
  Table[ReplacePart[{0,0,0}, i->s], {i,3}, {s,{-1,1}}],
  1
];

edges = Flatten[
  Table[
    With[{inds=DeleteCases[Range[3],z]},
      Table[
        ReplacePart[
          {0,0,0},
          {
            inds[[1]]->s1/Sqrt[2],
            inds[[2]]->s2/Sqrt[2]
          }
        ],
        {s1,{-1,1}},
        {s2,{-1,1}}
      ]
    ],
    {z,3}
  ],
  2
];

corners = Tuples[{-1/Sqrt[3],1/Sqrt[3]},3];
pts = Join[axes,edges,corners];

wts = Join[
  ConstantArray[1/21,6],
  ConstantArray[4/105,12],
  ConstantArray[9/280,8]
];

oddDF[n_Integer] := If[n<=0,1,Product[k,{k,n,1,-2}]];
sphereAverage[e_List] :=
  If[AnyTrue[e,OddQ],0,
    Times@@(oddDF[#-1]& /@ e)/oddDF[Total[e]+1]
  ];
pow0[x_,n_Integer] := If[n==0,1,x^n];
monomial[p_List,e_List] := Times@@MapThread[pow0,{p,e}];

exponents = Select[Tuples[Range[0,7],3],Total[#]<=7&];
residuals = Table[
  Together[
    Sum[wts[[q]] monomial[pts[[q]],e],{q,Length[pts]}]
    - sphereAverage[e]
  ],
  {e,exponents}
];

<|
  "PointCount" -> Length[pts],
  "WeightSum" -> Total[wts],
  "MonomialCount" -> Length[exponents],
  "NonzeroResidualCount" -> Count[residuals,_?(#=!=0&)],
  "SecondMoment" -> Together[
    Sum[wts[[q]] Outer[Times,pts[[q]],pts[[q]]],{q,26}]
  ],
  "SixthMomentExamples" -> <|
    "x6" -> Sum[wts[[q]] pts[[q,1]]^6,{q,26}],
    "x4y2" -> Sum[
      wts[[q]] pts[[q,1]]^4 pts[[q,2]]^2,{q,26}
    ],
    "x2y2z2" -> Sum[
      wts[[q]] Times@@(pts[[q]]^2),{q,26}
    ]
  |>
|>
