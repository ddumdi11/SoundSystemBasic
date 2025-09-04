import tkinter as tk
from tkinter import ttk, messagebox

try:
    from audio import windows as win
except Exception:  # pragma: no cover
    win = None  # type: ignore


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Sound System Basic – Stufe 1")
        self.geometry("1100x600")

        self.playback_devices: list[dict] = []
        self.recording_devices: list[dict] = []

        self._build_ui()
        self.refresh_devices()

    def _build_ui(self) -> None:
        # Top controls: refresh + status
        top = ttk.Frame(self)
        top.pack(fill="x", padx=8, pady=6)

        self.btn_refresh = ttk.Button(top, text="Aktualisieren", command=self.refresh_devices)
        self.btn_refresh.pack(side="left")

        self.status_var = tk.StringVar(value="Bereit.")
        self.lbl_status = ttk.Label(top, textvariable=self.status_var)
        self.lbl_status.pack(side="left", padx=12)

        # Main panes
        panes = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        panes.pack(fill="both", expand=True, padx=8, pady=6)

        # Playback pane
        frame_pb = ttk.Labelframe(panes, text="Wiedergabegeräte (Playback)")
        panes.add(frame_pb, weight=1)

        self.lb_playback = tk.Listbox(frame_pb, exportselection=False)
        self.lb_playback.pack(fill="both", expand=True, padx=6, pady=(6, 0))
        # Horizontal scrollbar for long entries
        self.pb_scroll_x = ttk.Scrollbar(frame_pb, orient=tk.HORIZONTAL, command=self.lb_playback.xview)
        self.lb_playback.configure(xscrollcommand=self.pb_scroll_x.set)
        self.pb_scroll_x.pack(fill="x", padx=6, pady=(0, 6))
        # Selection info + copy id
        pb_info = ttk.Frame(frame_pb)
        pb_info.pack(fill="x", padx=6, pady=(0, 6))
        self.pb_name_var = tk.StringVar(value="Name: –")
        self.pb_id_var = tk.StringVar(value="ID: –")
        self.pb_default_var = tk.StringVar(value="Standard: –")
        ttk.Label(pb_info, textvariable=self.pb_name_var).pack(side="left")
        ttk.Label(pb_info, textvariable=self.pb_id_var).pack(side="left", padx=12)
        ttk.Button(pb_info, text="ID kopieren", command=self.copy_pb_id).pack(side="right")
        ttk.Label(pb_info, textvariable=self.pb_default_var).pack(side="right", padx=12)

        btns_pb = ttk.Frame(frame_pb)
        btns_pb.pack(fill="x", padx=6, pady=6)
        ttk.Button(btns_pb, text="Als Standard setzen", command=self.set_default_playback).pack(side="left")

        # Recording pane
        frame_rec = ttk.Labelframe(panes, text="Aufnahmegeräte (Recording)")
        panes.add(frame_rec, weight=1)

        self.lb_recording = tk.Listbox(frame_rec, exportselection=False)
        self.lb_recording.pack(fill="both", expand=True, padx=6, pady=(6, 0))
        # Horizontal scrollbar for long entries
        self.rec_scroll_x = ttk.Scrollbar(frame_rec, orient=tk.HORIZONTAL, command=self.lb_recording.xview)
        self.lb_recording.configure(xscrollcommand=self.rec_scroll_x.set)
        self.rec_scroll_x.pack(fill="x", padx=6, pady=(0, 6))
        # Selection info + copy id
        rec_info = ttk.Frame(frame_rec)
        rec_info.pack(fill="x", padx=6, pady=(0, 6))
        self.rec_name_var = tk.StringVar(value="Name: –")
        self.rec_id_var = tk.StringVar(value="ID: –")
        self.rec_default_var = tk.StringVar(value="Standard: –")
        ttk.Label(rec_info, textvariable=self.rec_name_var).pack(side="left")
        ttk.Label(rec_info, textvariable=self.rec_id_var).pack(side="left", padx=12)
        ttk.Button(rec_info, text="ID kopieren", command=self.copy_rec_id).pack(side="right")
        ttk.Label(rec_info, textvariable=self.rec_default_var).pack(side="right", padx=12)

        btns_rec = ttk.Frame(frame_rec)
        btns_rec.pack(fill="x", padx=6, pady=6)
        ttk.Button(btns_rec, text="Als Standard setzen", command=self.set_default_recording).pack(side="left")

        # Bottom controls: volume, mute, test tone
        bottom = ttk.Labelframe(self, text="Systemlautstärke")
        bottom.pack(fill="x", padx=8, pady=6)

        inner = ttk.Frame(bottom)
        inner.pack(fill="x", padx=6, pady=6)

        ttk.Label(inner, text="Lautstärke:").pack(side="left")
        self.vol_var = tk.IntVar(value=35)
        self.scale_vol = ttk.Scale(inner, from_=0, to=100, orient=tk.HORIZONTAL, command=self._on_volume_move)
        self.scale_vol.pack(side="left", fill="x", expand=True, padx=8)

        self.lbl_vol = ttk.Label(inner, width=4, anchor="e", text=f"{self.vol_var.get():d}")
        self.lbl_vol.pack(side="left")

        self.mute_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(inner, text="Mute", variable=self.mute_var, command=self._on_mute_toggle).pack(side="left", padx=12)

        ttk.Button(inner, text="Testton", command=self.test_tone).pack(side="left")

    def set_status(self, text: str) -> None:
        self.status_var.set(text)

    def refresh_devices(self) -> None:
        if win is None:
            messagebox.showerror("Fehler", "Audio-Modul nicht verfügbar.")
            return
        try:
            self.playback_devices = win.list_playback_devices()
            self.recording_devices = win.list_recording_devices()
        except Exception as e:  # pragma: no cover
            self.playback_devices = []
            self.recording_devices = []
            self.set_status(f"Fehler beim Lesen der Geräte: {type(e).__name__}")
            return

        # Determine defaults for star marking
        try:
            pb_def_id = win.get_default_playback_id() if win else None
            rec_def_id = win.get_default_recording_id() if win else None
        except Exception:
            pb_def_id = None
            rec_def_id = None

        self.lb_playback.delete(0, tk.END)
        for d in self.playback_devices:
            name = d.get('name') or '(Unbenannt)'
            is_def = (d.get('id') == pb_def_id)
            label = f"★ {name}" if is_def else name
            self.lb_playback.insert(tk.END, label)

        self.lb_recording.delete(0, tk.END)
        for d in self.recording_devices:
            name = d.get('name') or '(Unbenannt)'
            is_def = (d.get('id') == rec_def_id)
            label = f"★ {name}" if is_def else name
            self.lb_recording.insert(tk.END, label)

        # Scroll lists to top for consistent first view
        try:
            self.lb_playback.yview_moveto(0.0)
            self.lb_recording.yview_moveto(0.0)
        except Exception:
            pass

        # Bind selection updates
        self.lb_playback.bind("<<ListboxSelect>>", self._on_select_playback)
        self.lb_recording.bind("<<ListboxSelect>>", self._on_select_recording)

        # Try to auto-select current defaults and show them
        pb_def = pb_def_id
        rec_def = rec_def_id

        self._select_by_id("playback", pb_def)
        self._select_by_id("recording", rec_def)
        self._update_default_labels(pb_def, rec_def)

        self.set_status(f"Geräte aktualisiert: {len(self.playback_devices)} Wiedergabe, {len(self.recording_devices)} Aufnahme")

    def _selected_device(self, which: str) -> dict | None:
        lb = self.lb_playback if which == "playback" else self.lb_recording
        data = self.playback_devices if which == "playback" else self.recording_devices
        try:
            idx = lb.curselection()
            if not idx:
                return None
            i = idx[0]
            return data[i]
        except Exception:
            return None

    def _norm_id(self, s: str | None) -> str:
        if not s:
            return ""
        return "".join(ch for ch in s if ch.isalnum()).lower()

    def _select_by_id(self, which: str, device_id: str | None) -> None:
        if not device_id:
            return
        data = self.playback_devices if which == "playback" else self.recording_devices
        lb = self.lb_playback if which == "playback" else self.lb_recording
        norm_target = self._norm_id(device_id)
        for idx, d in enumerate(data):
            if self._norm_id(d.get("id")) == norm_target:
                try:
                    lb.selection_clear(0, tk.END)
                except Exception:
                    pass
                lb.selection_set(idx)
                lb.see(idx)
                if which == "playback":
                    self._on_select_playback()
                else:
                    self._on_select_recording()
                break

    def _update_default_labels(self, pb_id: str | None, rec_id: str | None) -> None:
        def find_name(data, id_):
            if not id_:
                return "–"
            target = self._norm_id(id_)
            for d in data:
                if self._norm_id(d.get("id")) == target:
                    return d.get("name", "–")
            return "–"

        self.pb_default_var.set(f"Standard: {find_name(self.playback_devices, pb_id)}")
        self.rec_default_var.set(f"Standard: {find_name(self.recording_devices, rec_id)}")

    def _on_select_playback(self, _evt=None) -> None:
        dev = self._selected_device("playback")
        if not dev:
            self.pb_name_var.set("Name: –")
            self.pb_id_var.set("ID: –")
            return
        self.pb_name_var.set(f"Name: {dev.get('name','?')}")
        self.pb_id_var.set(f"ID: {dev.get('id','?')}")

    def _on_select_recording(self, _evt=None) -> None:
        dev = self._selected_device("recording")
        if not dev:
            self.rec_name_var.set("Name: –")
            self.rec_id_var.set("ID: –")
            return
        self.rec_name_var.set(f"Name: {dev.get('name','?')}")
        self.rec_id_var.set(f"ID: {dev.get('id','?')}")

    def set_default_playback(self) -> None:
        dev = self._selected_device("playback")
        if not dev:
            self.set_status("Kein Wiedergabegerät ausgewählt.")
            return
        ok = win.set_default_playback(dev.get("id") or dev.get("name", ""))
        self.set_status(
            f"Wiedergabe-Standard gesetzt: {dev.get('name')}" if ok else "Fehler beim Setzen des Wiedergabe-Standards."
        )
        # Short delay to let the system apply before refreshing
        self.after(400, self._refresh_defaults_after_set)
        try:
            pb_def = win.get_default_playback_id()
            self._select_by_id("playback", pb_def)
            self._update_default_labels(pb_def, win.get_default_recording_id())
        except Exception:
            pass

    def set_default_recording(self) -> None:
        dev = self._selected_device("recording")
        if not dev:
            self.set_status("Kein Aufnahmegerät ausgewählt.")
            return
        ok = win.set_default_recording(dev.get("id") or dev.get("name", ""))
        self.set_status(
            f"Aufnahme-Standard gesetzt: {dev.get('name')}" if ok else "Fehler beim Setzen des Aufnahme-Standards."
        )
        # Short delay to let the system apply before refreshing
        self.after(400, self._refresh_defaults_after_set)

    def _refresh_defaults_after_set(self) -> None:
        try:
            pb_def = win.get_default_playback_id() if win else None
            rec_def = win.get_default_recording_id() if win else None
            # Update labels
            self._update_default_labels(pb_def, rec_def)
            # Reselect defaults in lists and update star markers by reloading list labels
            self.refresh_devices()
        except Exception:
            pass

    def _on_volume_move(self, _value: str) -> None:
        try:
            # ttk.Scale passes string, cast to int
            val = int(float(_value))
        except Exception:
            return
        self.lbl_vol.configure(text=f"{val:d}")
        # Apply on release only? For responsiveness, apply continuously is fine.
        if win is not None:
            win.set_master_volume(val)

    def _on_mute_toggle(self) -> None:
        if win is not None:
            win.mute_master(bool(self.mute_var.get()))
        self.set_status("Mute geändert.")

    def test_tone(self) -> None:
        if win is not None:
            win.play_test_tone()
        self.set_status("Testton abgespielt.")

    def copy_pb_id(self) -> None:
        dev = self._selected_device("playback")
        if not dev:
            return
        did = dev.get("id") or ""
        self.clipboard_clear()
        self.clipboard_append(did)
        self.set_status("Wiedergabe-ID kopiert.")

    def copy_rec_id(self) -> None:
        dev = self._selected_device("recording")
        if not dev:
            return
        did = dev.get("id") or ""
        self.clipboard_clear()
        self.clipboard_append(did)
        self.set_status("Aufnahme-ID kopiert.")


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":  # pragma: no cover
    main()
