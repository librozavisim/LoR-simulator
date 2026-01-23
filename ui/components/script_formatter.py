from ui.icons import get_icon_html

def _format_script_text(script_id: str, params: dict) -> str:
    """
    Форматирует технические ID скриптов в читаемый текст с иконками.
    """
    def get_val(p): return p.get("base", p.get("amount", p.get("stack", 0)))

    def get_scale_text(p):
        stat = p.get("stat")
        if stat and stat != "None":
            factor = p.get("factor", 1.0)
            diff = p.get("diff", False)
            sign = "+" if factor >= 0 else ""
            diff_txt = " (Diff)" if diff else ""
            return f" [{sign}{factor}x {stat}{diff_txt}]"
        return ""

    def get_time_text(p):
        dur = int(p.get("duration", 0))
        dly = int(p.get("delay", 0))
        parts = []
        if dur > 1: parts.append(f"⏳{dur}")
        if dly > 0: parts.append(f"⏰{dly}")
        return f" ({', '.join(parts)})" if parts else ""

    # === ЛЕЧЕНИЕ / РЕСУРСЫ ===
    if script_id in ["restore_hp", "restore_resource"]:
        res_type = params.get("type", "hp").lower()
        if script_id == "restore_hp": res_type = "hp"
        icon = get_icon_html(res_type)
        val = get_val(params)
        scale = get_scale_text(params)
        return f"{icon} {res_type.upper()}: {val}{scale}"

    elif script_id in ["restore_sp", "restore_sp_percent"]:
        val = get_val(params)
        icon = get_icon_html("sp")
        return f"{icon} SP: {val}"

    # === СТАТУСЫ ===
    elif script_id == "apply_status":
        status_key = params.get("status", "???").lower()
        status_label = status_key.capitalize()
        icon = get_icon_html(status_key)
        val = get_val(params)
        scale = get_scale_text(params)
        time_info = get_time_text(params)
        target = params.get("target", "target")
        tgt_map = {"self": "себя", "target": "цель", "all": "всех", "all_allies": "союзников"}
        tgt_str = f" ({tgt_map.get(target, target)})"
        return f"{icon} {status_label}: {val}{scale}{time_info}{tgt_str}"

    # === УРОН / МОЩЬ ===
    elif script_id == "modify_roll_power":
        val = get_val(params)
        scale = get_scale_text(params)
        return f"🎲 Power: {val}{scale}"

    elif script_id == "deal_effect_damage":
        dtype = params.get("type", "hp").lower()
        icon = get_icon_html(dtype)
        val = get_val(params)
        scale = get_scale_text(params)
        return f"💔 Dmg ({icon}): {val}{scale}"

    elif script_id == "steal_status":
        status = params.get("status", "???")
        return f"✋ Украсть {status}"

    return f"🔧 {script_id} {params}"