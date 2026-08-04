# Memory and orbit layout

State count: 17 x 26 = 442.
Complete unordered edges: 97,461.
Recommended active edges: 93,925.
Complete scalar physics orbits: 1,972.
Active scalar physics orbits: 1,836.
Complete weighted conductance orbits: 3,009.
Active weighted conductance orbits: 2,601.

The scalar local kernel is evaluated once per physics orbit.
Explicit edge action is retained because the radiation state is anisotropic.

## Byte counts

```json
{
  "dense_442x442_float64_bytes": 1562912,
  "symmetric_packed_including_diagonal_float64_bytes": 783224,
  "all_offdiagonal_edge_weights_float64_bytes": 779688,
  "edge_endpoints_two_uint16_bytes": 389844,
  "two_orbit_maps_uint16_bytes": 389844,
  "active_flag_uint8_bytes": 97461,
  "active_CSR_indices_uint16_bytes": 375700,
  "active_CSR_edge_ids_uint32_bytes": 751400,
  "active_CSR_indptr_uint32_bytes": 1772,
  "physics_orbit_weight_table_float64_bytes": 15776,
  "weighted_orbit_weight_table_float64_bytes": 24072
}
```
