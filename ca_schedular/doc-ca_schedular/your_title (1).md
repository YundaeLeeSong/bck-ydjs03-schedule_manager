# Calendar Manager App – PyQt5 Implementation Plan

## 1. Overview  
A **standalone**, Python-only desktop app using **PyQt5** that provides a Google-Calendar-style UI.  
Users can **import** existing `.ics` files, **toggle** whole calendars on/off (unique colors, overlap stacking), **drag** events in 15-minute increments/decrements, and **save** or **discard** all changes. Only **update** operations are supported—no create/delete of events beyond what’s already in the files.

---

## 2. User Stories  
1. **File Toggle & Coloring**  
   - See a list of `.ics` files with checkboxes.  
   - Toggle each calendar on/off; enabled calendars’ events get distinct colors; overlapping events stack side-by-side.  
2. **Fine-grained Drag & Drop**  
   - Drag event blocks to new days/times in ±15-minute steps.  
3. **Save Adjustments**  
   - Save overwrites the original `.ics` files with updated `DTSTART`/`DTEND` timestamps.  
4. **Discard Changes (Back/Exit)**  
   - “Discard” reverts all unsaved modifications by reloading from disk.

---

## 3. High-Level Architecture  
```plaintext
┌─────────────────┐        ┌───────────────┐        ┌───────────────────┐
│ .ics File Store │──(1)──>│  Core Module  │<───────│  GUI (PyQt5)      │
│  (DATA_DIR/*)   │        │ (Parser, I/O) │──(2)──>│                   │
└─────────────────┘        └───────────────┘        └───────────────────┘
       ▲   (5)                                           │    ▲    ▲
       │                                                (4)  │    │
      (3)                                                    │    │
       │                                                User Drag & Drop  
┌─────────────────┐                                       Save/Discard  
│ .ics File Store │<───────────────────────────────────────┘          
└─────────────────┘
```
1. **Import**: Core reads & parses `.ics` at startup or “Refresh.”  
2. **Event API**: Core exposes in-memory `Event` list, filtered by `enabled` flags.  
3. **Discard**: GUI tells Core to reload from disk.  
4. **Save**: GUI invokes Core to rewrite `.ics` files.  
5. **Persistence**: Disk only updated when “Save” completes.

---

## 4. Technology Stack  
- **Language**: Python 3.10+  
- **GUI**: PyQt5  
  - Main window: `QMainWindow`  
  - File list: `QListWidget` with checkboxes  
  - Calendar view: `QGraphicsView` + custom `QGraphicsScene`  
  - Event objects: subclassed `QGraphicsRectItem` with drag enabled  
  - Controls: `QPushButton` for Save, Discard, Refresh  
- **ICS Parsing & Serialization**: [`ics.py`](https://github.com/C4pt000/ics.py)  
- **Packaging**: PyInstaller → single executable  

---

## 5. Data Model  
```python
class Event:
    def __init__(self, uid: str, title: str, description: str,
                 start: datetime, end: datetime,
                 source_file: str, enabled: bool, color: QColor):
        self.uid = uid
        self.title = title
        self.description = description
        self.start = start      # datetime.datetime (UTC)
        self.end = end
        self.source_file = source_file
        self.enabled = enabled
        self.color = color      # Qt QColor instance
```

---

## 6. Detailed Feature Breakdown  

### 6.1. File List & Toggle  
- **`QListWidget`**  
  - One `QListWidgetItem` per `.ics` file, with checkbox.  
  - On toggle: set `enabled` on all Events from that file, assign a distinct `QColor` (e.g., HSL distribution).  
- **“Refresh” Button**  
  - Re-scan directory, update list and Core state.

### 6.2. Calendar View & Overlap Rendering  
- **`QGraphicsScene`**  
  - Seven vertical columns (Mon–Sun), each subdivided into 96 rows (15-min slots).  
  - Grid lines drawn once.  
- **`CalendarEventItem`** (subclass `QGraphicsRectItem`)  
  - Rectangle sized/positioned by `(start, end)`; brush set to `Event.color`.  
  - Contains a `QGraphicsTextItem` child for `title`.  
  - **Overlap**: on add, calculate horizontal offset & width = columnWidth ÷ maxOverlap.  

### 6.3. Drag-and-Drop Rescheduling  
- Enable `ItemIsMovable` & override `mouseReleaseEvent` on `CalendarEventItem`.  
- On drag end:  
  1. Compute `deltaY` in pixels → minutes = `deltaY / slotHeight * 15`.  
  2. Round to nearest 15.  
  3. Update `Event.start`/`end`.  
  4. Snap the item’s Y-pos to the grid.  
  5. Mark Core state as “dirty.”

### 6.4. Save & Overwrite  
- **“Save” Button** triggers Core’s `write_all()` method:  
  1. For each `source_file`, read original `.ics` raw text.  
  2. For each `VEVENT`, locate `UID:` line → replace its `DTSTART`/`DTEND`.  
  3. Overwrite file with `open(path, "w")`.  
- Show a `QMessageBox` on success/failure.

### 6.5. Discard Changes  
- **“Discard” Button** or window close event:  
  - If `dirty`, prompt via `QMessageBox`: “Discard all unsaved changes?”  
  - On confirm, clear scene, reload Core events from disk, and redraw.

---

## 7. Error Handling & Edge Cases  
- **File Locking**: Use Python’s `threading.Lock` around `write_all()`.  
- **Bounds Checking**: Prevent dragging outside the current week’s columns or before 00:00 or after 23:45.  
- **Time-Zone**: Treat all parsed dates as UTC; convert to local when mapping to scene.  
- **Unsaved Exit**: Reimplement `closeEvent()` in `QMainWindow` to warn about dirty state.

---

## 8. Testing Strategy  
- **Unit Tests (pytest)**  
  - `.ics` parse & serialize round-trip.  
  - Pixel-to-minute and minute-to-pixel snap logic.  
- **Manual GUI Testing**  
  - Toggle file visibility, overlapping render, drag/drop ±15 min, save & reopen to verify persistence, discard workflow.

---

## 9. Roadmap & Milestones  
| Milestone                    | Duration | Deliverables                                |
| ---------------------------- | -------- | ------------------------------------------- |
| 1. Core ICS I/O Module       | 1 week   | `ics_parser.py`, `Event` model, tests      |
| 2. PyQt5 Shell & File List   | 1 week   | `QMainWindow`, `QListWidget` toggle logic   |
| 3. Calendar Grid & Rendering | 2 weeks  | `QGraphicsScene`, grid, overlap stacking    |
| 4. Drag-&-Drop Logic         | 1 week   | Movable `CalendarEventItem`, snap handling  |
| 5. Save & Discard Actions    | 1 week   | `write_all()`, confirm dialogs              |
| 6. Testing & Packaging       | 1 week   | Test suite, PyInstaller build               |

---

> *All-Python, PyQt5-powered calendar editor—update-only, overlap-aware, with Save & Discard controls!*  
