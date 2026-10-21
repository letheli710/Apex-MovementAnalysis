# Unity batch runs - M1 replay pipeline

Unity 6000.6.5f1, Windows 11, batch mode. Project `HSD-Unity` (local git repo, not pushed). Paths are placeholders: `<HSD-Unity>` = the Unity project, `<research-repo>` = Apex-MovementAnalysis, `<logs>` = a local scratch folder (full logs not copied).

## Commands

```
Unity.exe -batchmode -quit -createProject <HSD-Unity> -logFile <logs>\create.log
Unity.exe -batchmode -projectPath <HSD-Unity> -runTests -testPlatform EditMode -testResults <logs>\tests.xml -logFile <logs>\tests.log
Unity.exe -batchmode -projectPath <HSD-Unity> -executeMethod HSD.R5Replay.Editor.BatchReplay.Run -trial <research-repo>\research\phase2-local\m1\trials\M1_r41 -trial <...>\M1_r42 -trial <...>\M1_r46 -out <research-repo>\research\phase2-local\m1\unity -logFile <logs>\replay.log
```

Process exit codes: createProject 0, runTests 0, BatchReplay 0.

## 1. Project creation (create.log)

```
Built from '6000.6/staging' branch; Version is '6000.6.5f1 (3ff58d469c8a) revision 4191629'; Using compiler version '194234433'; Build Type 'Release'
[Package Manager] Done resolving packages in 3.71 seconds
[Package Manager] Registered 42 packages:
AssetDatabase: script compilation time: 10.329210s
```

`com.unity.test-framework` 1.8.0 (built-in package of this editor) was then added to Packages/manifest.json.

## 2. EditMode tests (tests.log, tests.xml)

```
Built from '6000.6/staging' branch; Version is '6000.6.5f1 (3ff58d469c8a) revision 4191629'; Using compiler version '194234433'; Build Type 'Release'
    com.unity.test-framework@1.8.0 (location: <HSD-Unity>\Library\PackageCache\com.unity.test-framework@80f691d4262b)
AssetDatabase: script compilation time: 0.593820s
UnityEditor.TestTools.TestRunner.CommandLineTest.Executer:InitializeAndExecuteRun (string[]) (at ./Library/PackageCache/com.unity.test-framework@80f691d4262b/UnityEditor.TestRunner/CommandLineTest/Executer.cs:53)
UnityEditor.TestTools.TestRunner.CommandLineTest.TestStarter:InitializeAndExecuteRun () (at ./Library/PackageCache/com.unity.test-framework@80f691d4262b/UnityEditor.TestRunner/CommandLineTest/TestStarter.cs:64)
(Filename: ./Library/PackageCache/com.unity.test-framework@80f691d4262b/UnityEditor.TestRunner/CommandLineTest/Executer.cs Line: 53)
Saving results to: <logs>\tests.xml
Test run completed. Exiting with code 0 (Ok). Run completed.
UnityEditor.TestTools.TestRunner.CommandLineTest.Executer:ExitApplication (UnityEditor.TestTools.TestRunner.CommandLineTest.Executer/ReturnCodes,string) (at ./Library/PackageCache/com.unity.test-framework@80f691d4262b/UnityEditor.TestRunner/CommandLineTest/Executer.cs:81)
UnityEditor.TestTools.TestRunner.CommandLineTest.Executer:ExitIfRunIsCompleted () (at ./Library/PackageCache/com.unity.test-framework@80f691d4262b/UnityEditor.TestRunner/CommandLineTest/Executer.cs:74)
(Filename: ./Library/PackageCache/com.unity.test-framework@80f691d4262b/UnityEditor.TestRunner/CommandLineTest/Executer.cs Line: 81)
```

Result: **Passed** - total 26, passed 26, failed 0, skipped 0, duration 0.098 s. (A first run failed 12/26 because the hand-written fixture trial.json had an invalid JSON escape; the fixture was fixed, no code change.)

| test | result |
|---|---|
| AlignmentTests.DifferentCmdSequenceFails | Passed |
| AlignmentTests.LongerSimFailsLoudly | Passed |
| AlignmentTests.MatchingTraceAligns | Passed |
| AlignmentTests.ShorterSimFailsLoudly | Passed |
| MiniJsonTests.ParsesNestedObjectsArraysAndEscapes | Passed |
| MiniJsonTests.RejectsMalformedJson | Passed |
| MiniJsonTests.SerializeRoundTrips | Passed |
| ReferenceMotorTests.AirAccelerationIsCappedByAirSpeed | Passed |
| ReferenceMotorTests.GroundSpeedApproachesMaxSpeed | Passed |
| ReferenceMotorTests.GroundStopsWithDeceleration | Passed |
| ReferenceMotorTests.JumpApexMatchesJumpHeight | Passed |
| ReferenceMotorTests.JumpOnlyOnPressEdgeWhileGrounded | Passed |
| ReferenceMotorTests.JumpVelocityFormula | Passed |
| ReferenceMotorTests.ReplayIsDeterministic | Passed |
| SourceSpaceTests.AxisMappingIsMinusYZX | Passed |
| SourceSpaceTests.RoundTripAndScale | Passed |
| SourceSpaceTests.YawAndBasisVectors | Passed |
| TrialLoaderTests.LoadsSyntheticTrial | Passed |
| TrialLoaderTests.MoveScaleFromCourseNote | Passed |
| TrialLoaderTests.RejectsCmdGap | Passed |
| TrialLoaderTests.RejectsMissingColumn | Passed |
| TrialLoaderTests.RejectsNonConsecutiveStep | Passed |
| TrialLoaderTests.RejectsNonIncreasingCmd | Passed |
| TrialLoaderTests.RejectsNonIncreasingTime | Passed |
| TrialLoaderTests.RejectsWrongContract | Passed |
| TrialLoaderTests.UnitySpaceAccessorsUseContractMapping | Passed |

## 3. Batch replay (replay.log)

```
Built from '6000.6/staging' branch; Version is '6000.6.5f1 (3ff58d469c8a) revision 4191629'; Using compiler version '194234433'; Build Type 'Release'
AssetDatabase: script compilation time: 0.588547s
[R5Replay] M1_r41: 1225 steps, pos RMS 32.17 u (max 34.48), vel RMS 23.13 u/s (max 288.86); takeoff Δ0, land Δ+2, stop Δ0, apex 54.91→56.00 u, takeoff vz 282.25→284.77 u/s, peak speed 199.53→199.53 u/s
[R5Replay] M1_r42: 1225 steps, pos RMS 32.28 u (max 34.59), vel RMS 23.16 u/s (max 288.43); takeoff Δ0, land Δ+2, stop Δ0, apex 54.88→56.00 u, takeoff vz 282.01→284.62 u/s, peak speed 199.53→199.53 u/s
[R5Replay] M1_r46: 1225 steps, pos RMS 32.19 u (max 34.49), vel RMS 23.16 u/s (max 288.09); takeoff Δ0, land Δ+2, stop Δ0, apex 54.87→56.00 u, takeoff vz 281.96→284.59 u/s, peak speed 199.53→199.53 u/s
[R5Replay] wrote 3/3 trial reports to <research-repo>\research\phase2-local\m1\unity
[R5Replay] exit code 0
```

No compiler warnings or errors from the HSD.R5Replay assemblies in any run. The licensing client logs 'Access token is unavailable; failed to update' at every start; the licence still resolved and the runs completed.
