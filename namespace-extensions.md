# Namespace ownership & extension audit

How secorolab additions relate to the upstream **comp-rob2b** metamodels, and which
terms still need relocating. Upstream = `https://comp-rob2b.github.io/metamodels/…`;
secorolab = `https://secorolab.github.io/metamodels/…`.

## Convention

- **Do not define new terms (classes / predicates / individuals) in a comp-rob2b
  namespace.** secorolab does not own `comp-rob2b.github.io`, so inventing
  `map:PoseOrientationView`, `slv:CommandForwardingSolver`, etc. is squatting.
- **New secorolab terms go in a secorolab `*-ext` umbrella** mirroring the upstream
  path, with prefix `<base>-ext` — the same way `mot-ext` shadows `mot`:
  | upstream prefix → namespace | secorolab extension |
  |---|---|
  | `map` → `…/task/map#` | `map-ext` → `https://secorolab.github.io/metamodels/task/map#` |
  | `slv` → `…/task/solver-specification#` | `slv-ext` → `…secorolab…/task/solver-specification#` |
  | `cstr-hdl` → `…/task/constraint-handler#` | `cstr-hdl-ext` → `…secorolab…/task/constraint-handler#` |
  | `geom-op` → `…/geometry/spatial-operators#` | `geom-op-ext` → `…secorolab…/geometry/spatial-operators#` |
  | `rbdyn-op` → `…/newtonian-rigid-body-dynamics/operators#` | `rbdyn-op-ext` → `…secorolab…` |
- **Reusing upstream predicates is correct** — only *new* terms move. e.g.
  `map-ext:PoseOrientationView` still uses `map:superobject`/`subobject`/`axis`;
  `slv-ext:CommandForwardingSolver` still uses `slv:solver`/`attached-to`;
  `rbdyn-op-ext:AddQuantity` still uses `rbdyn-op:in1/in2/out`.

### Two exceptions / caveats

- **Stub namespaces are *not* squatting.** comp-rob2b publishes
  `geometry/structural-entities`, `kinematic-chain/*`, `newtonian-rigid-body-dynamics/
  structural-entities` & `…/coordinates` only as **empty `.json` stubs** (no
  machine-readable term definitions). Their core concepts — `Frame`, `Point`,
  `SimplicialComplex`, `KinematicChain`, `RigidBody`, `Joint`, `JointPositionCoordinate`,
  `Wrench`, `Mass`, … — are upstream vocabulary and are reused legitimately even though
  they don't appear in any upstream file. **Do not relocate these.**
- **`constraint-handler.shacl.ttl` is a deliberate "local replacement"** of the upstream
  `cstr_hdl` ontology, so its re-shaped upstream classes stay in `cstr_hdl`. Only
  genuinely-new controller types are extracted to `cstr-hdl-ext`.

## Audit method

Authoritative diff against a local comp-rob2b checkout (`src/comp-rob2b/metamodels`):
load every upstream `.ttl` + `.json` into one rdflib graph, collect all comp-rob2b
URIs, then diff against the comp-rob2b URIs emitted in `models/gen/*/*.json`. Only
namespaces backed by a **substantive** upstream `.ttl` give reliable results
(`geometry/{coordinates,spatial-operators,spatial-relations}`, `task/{map,constraint,
constraint-handler,solver-specification}`, `newtonian-rigid-body-dynamics/operators`).

## Done — established `*-ext` umbrellas

| umbrella | terms |
|---|---|
| `mot-ext` | `ConstraintConjunction`, `ConstraintDisjunction`, `has-constraint` |
| `map-ext` | `PoseOrientationView`, `PosePositionView`, `rotation`, `pose`, `ComputeRotationFromPose` |
| `slv-ext` | `CommandForwarding{Solver,Specification,Algorithm}`, `command-forwarding`, `control-signal`, `gravity-value` |
| `cstr-hdl-ext` | `FeedForwardController`, `reference-signal` |
| `rbdyn-op-ext` | `AddQuantity` |

`map-ext:PosePositionView` also fixed a conformance bug: upstream `map:PoseCoordinateView`
mandates `map:axis`, so a whole-vector position view cannot be one.

## Remaining squatters to relocate

Verified secorolab-invented, still emitted under comp-rob2b prefixes:

| target umbrella | terms | notes |
|---|---|---|
| **`geom-op-ext`** ⚠️ large | `InvertPose`, `InvertAngle`, `PoseDiffEvaluator`, `PlanarAngleFromDirections`, `AddVelocityTwist`, `AddAccelerationTwist`, `TransformVelocityTwistToDistal`, `TransformAccelerationTwistToDistal`, `RotateVelocityTwistToProximalWithPose`, `RotateDirectionDistalToProximalWithPose` + predicates `out`, `from`, `in`, `to`, `absolute-velocity`, `relative-velocity`, `from-directions` | comp-rob2b `spatial-operators` only defines `ComposePose` + the `Pose→{Angle,Direction,LinearDistance}` projections (+ `in1/in2/composite/pose/distance/direction/angle/axis/x/y/z`). **The rest of the operator layer is secorolab** and threads through the computational-graph / closure machinery — relocate as one coordinated, well-tested unit. |
| **`geom-coord-ext`** | `EulerAngles`, `axes-sequence`, `has-coordinate`, `angle-axis` | also touches the secorolab `geometry/geometry.shacl.ttl` shapes |
| **`geom-rel-ext`** | `Direction` | small |
| **`cstr-ext`** | `AngleConstraint`, `DistanceConstraint`, `OrientationConstraint`, `PoseConstraint`, `LessThanConstraint` | emitted constraint subtypes; read by IR constraint classification |
| **`cstr-hdl-ext`** 🟡 | `control-mode`, `evaluators`, `monitors-until`, `JointTorque` | "replacement" gray area; `control-mode` is read by `motion-spec-check`. Decide whether to move (consistent with `FeedForwardController`) or keep as part of the local replacement. |

## Couldn't verify

- `app:order` (`comp-rob2b…/application/order`) is emitted, but comp-rob2b publishes no
  `application` `.ttl`, so membership is undeterminable here. If it's a secorolab addition it
  should become `app-ext:order`; confirm against the upstream application metamodel first.

## Confirmed non-issues (do not re-flag)

- Stub-namespace core types (see caveat above): `geom-ent:*`, `kc:*`, `kc-stat:*`,
  `rbdyn-ent:*`, `rbdyn-coord:as-seen-by`.
- Upstream and correctly reused: `geom-rel:Position`/`Orientation`/`Pose`,
  `cstr:Constraint`/`EqualityConstraint`/`PositionConstraint`, all reused upstream
  predicates listed under *Convention*.
