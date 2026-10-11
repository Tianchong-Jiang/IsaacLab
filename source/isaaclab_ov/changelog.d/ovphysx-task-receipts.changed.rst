* **Breaking:** Migrated runtime attachment, updates, clone replay, and stage
  teardown to the OVPhysX task API. Install a runtime exposing ``PhysX.wait_task()``. Custom Python
  callers must pass the complete ``Task`` receipt returned by ``attach_ovstage()``,
  ``update_from_ovstage()``, ``clone()``, or ``detach_ovstage()`` to ``wait_task()``
  instead of using integer operation indices with ``wait_op()``. Task execution
  failures are collected before startup, gravity publication, stage reuse, or cleanup continues.
