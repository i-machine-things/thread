# THREAD

A small Tkinter app that generates Fanuc-style lathe G-code for single-point threading (external or internal),
using the `G32` threading cycle. Enter your thread parameters, hit Generate, and it writes a ready-to-run `.nc`
file to `output/`.

## Running it

Run from source:

```
pip install -r requirements.txt
python3 main.py
```

Requires `numpy` and Tk (`python3-tk` on Debian/Ubuntu if it's not already available).

To build a standalone binary instead:

```
pip install pyinstaller
pyinstaller main.spec
```

This produces `dist/thread` (Linux) or `dist/thread.exe` (Windows). `dist/` isn't tracked in this repo — grab
a prebuilt binary from [Releases](../../releases) instead of building your own, or build it yourself as above.

## Fields

| Field | Meaning |
|---|---|
| Units | `Inch` (`G20`) or `MM` (`G21`) |
| Thread Class | `External` or `Internal` |
| Major Diameter | Nominal thread OD (external) or bore ID (internal) |
| Thread Pitch | Feed rate per revolution for the `G32` move |
| Z Initial / Z Final Position | Start and end Z of the threading pass |
| Number of Passes | How many infeed passes to split the total thread depth across |
| Infeed Angle | Compound infeed angle (half-angle) — e.g. 29.5° on a 60° thread form to load one flank instead of both |
| Thread Depth | Total radial depth of thread to cut |
| Flanking Infeed | When `Yes`, alternates a compound-angle pass with a straight radial pass each cycle instead of straight infeed only |
| Tool # | Tool number written into the `G50 ... T####` line |
| Work Offset | e.g. `54` for `G54` |
| Cutting Speed | Spindle speed (`G97 S...`, constant surface speed is not used) |

## Output

Files land in `output/`, named from the parameters themselves, e.g.:

```
External 0.375 X 0.0625 Inch 59.0 DEG THREAD.nc
```

Example output for a trivial (all-zero) external thread:

```
%
O1000 (External 0.0 X 0.0 Inch 0.0 DEG THREAD)
G20
G28 U0.0
G28 W0.0
G50 S250 T0000
G97 S100 M3 P11
G0 G54 X0.1 Z0.0
X0.0 Z0.0
G32 Z0.0 F0.0
G0 X0.1
Z0.0
G28 U0.0
G28 W0.0
M5
M30
%
```

Always review generated G-code before running it at the machine, as with any tool that writes code you're about
to cut metal with.

## Project layout

| File | Purpose |
|---|---|
| `main.py` | Entry point — GUI + `generate_code()` (the G-code generation logic) |
| `main.ui` | pygubu-designer source for the GUI layout (editable design source, not loaded at runtime) |
| `main.spec` | PyInstaller build spec |
| `requirements.txt` | Runtime dependencies (`numpy`; `tkinter`/`pathlib`/`os` are stdlib) |
