"""Respond to follow-up questions about MOXXI's systems."""

import re

from voice_settings import load_voice_settings


def respond_with_multitopic_context(message, context):
    """Answer a supported follow-up for the active topic."""

    if not isinstance(message, str) or context is None:
        return None

    text = message.casefold().strip().rstrip("?.!")

    topic = context.get_topic()

    introductions = {
        "tell me about your voice": (
            "My voice system lets me speak using offline "
            "speech engines, sugar! We're developing it "
            "to give me a warm, playful personality."
        ),
        "tell me about your memory": (
            "My memory system helps me remember your saved "
            "name and search our conversation history, "
            "darling. We're expanding it step by step."
        ),
        "tell me about your software": (
            "I'm powered by Python software, sugar! "
            "My conversation engine connects my knowledge, "
            "memory, personality, and voice systems."
        ),
    }

    introduction = introductions.get(text)
    if introduction is not None:
        return introduction

    introduction_patterns = {
        "voice": (
            r"^(?:can you )?tell me about your voice$",
            r"^i(?:'d| would) like to know about your voice$",
            r"^explain your voice(?: system)?$",
            r"^what about your voice$",
        ),
        "memory": (
            r"^(?:can you )?tell me about your memory$",
            r"^i(?:'d| would) like to know about your memory$",
            r"^explain your memory(?: system)?$",
            r"^what about your memory$",
        ),
        "software": (
            r"^(?:can you )?tell me about your software$",
            r"^i(?:'d| would) like to know about your software$",
            r"^explain your software(?: system)?$",
            r"^what about your software$",
        ),
    }

    for subject, patterns in introduction_patterns.items():
        if topic != subject:
            continue

        if any(re.search(pattern, text) for pattern in patterns):
            return introductions[f"tell me about your {subject}"]

    if topic == "voice":
        if re.search(
            r"\b(?:which|what) voice are you using\b", text
        ):
            settings = load_voice_settings()
            engine = settings.get("engine", "windows")

            if not settings.get("enabled", True):
                return "My voice output is currently disabled, sugar."

            if engine == "piper":
                return (
                    "I'm configured to use Piper Amy, darling! "
                    "She's my current offline voice."
                )

            if engine == "windows":
                return (
                    "I'm configured to use my Windows speech "
                    "engine right now, sugar."
                )

            return "I couldn't identify my configured voice engine."

        if re.search(r"\bcan you speak offline\b", text):
            return (
                "You bet, sugar! My speech system can run "
                "locally without an internet connection."
            )

    if topic == "memory":
        if re.search(r"\bwhat can you remember\b", text):
            return (
                "I can remember your saved name and search "
                "our recorded conversations, darling. "
                "My memory system is still growing."
            )

        if re.search(
            r"\bdo you save our conversations\b", text
        ):
            return (
                "Yes, sugar. My conversation history system "
                "can save our exchanges locally."
            )

    if topic == "software":
        if re.search(
            r"\bwhat language are you written in\b", text
        ):
            return (
                "I'm written primarily in Python, darling! "
                "That's what powers my conversation and "
                "memory systems."
            )

        if re.search(
            r"\bcan you control the robot yet\b", text
        ):
            return (
                "Not yet, sugar. My physical robot controls "
                "are still on our development roadmap."
            )

    # Calculate remaining battery capacity from a Windows report.
    if (
        topic == "laptop"
        and context.get_subtopic() == "charging"
        and context.get_troubleshooting_step()
        in ("waiting_for_battery_capacities", "waiting_for_battery_report")
    ):
        capacity_pattern = r"([0-9][0-9,]*)\s*mwh"
        design_match = re.search(
            r"design\s+capacity\s*[:=]?\s*" + capacity_pattern,
            text,
        )
        full_match = re.search(
            r"full\s+charge\s+capacity\s*[:=]?\s*" + capacity_pattern,
            text,
        )

        if design_match and full_match:
            design = int(design_match.group(1).replace(",", ""))
            full = int(full_match.group(1).replace(",", ""))

            if design <= 0 or full <= 0 or full > design * 2:
                return (
                    "Those capacity numbers don't look right, sugar. "
                    "Please double-check Design Capacity and Full "
                    "Charge Capacity in mWh."
                )

            health = full / design * 100
            context.clear_troubleshooting_step()

            return (
                f"Alright, sugar! Your battery retains approximately "
                f"{health:.1f}% of its original design capacity. "
                f"That's based on {full:,} mWh full charge capacity "
                f"compared with {design:,} mWh design capacity. "
                "This measures capacity retention, not the battery's "
                "current charge percentage. It doesn't diagnose the "
                "cause of a charging problem by itself."
            )

        return (
            "I need both measurements, darling. Please enter them "
            "like this: Design Capacity: 50000 mWh, "
            "Full Charge Capacity: 40000 mWh."
        )

    # Handle Windows battery report questions.
    if (
        topic == "laptop"
        and context.get_subtopic() == "charging"
        and context.get_troubleshooting_step()
        == "checking_battery_report"
    ):
        answer = re.sub(r"\s+", " ", text.replace(",", " ")).strip()

        if answer in (
            "yes", "yes i have", "yes i did",
            "yes i generated one", "i have a report",
            "i already have one",
        ):
            context.set_troubleshooting_step(
                "waiting_for_battery_capacities"
            )
            return (
                "Perfect, sugar! Open your Windows battery "
                "report and look under Installed batteries. "
                "Find Design Capacity and Full Charge Capacity. "
                "What numbers does the report show for each?"
            )

        if answer in (
            "no", "no i haven't", "no i have not",
            "no i didn't", "not yet",
            "i don't have one", "i have not generated one",
        ):
            context.set_troubleshooting_step(
                "waiting_for_battery_report"
            )
            return (
                "No problem, darling! Open PowerShell and run "
                "powercfg /batteryreport. Windows will tell you "
                "where it saved the HTML report. Open that file "
                "and look under Installed batteries for Design "
                "Capacity and Full Charge Capacity. Let me know "
                "when you have those numbers."
            )

    # Handle battery error codes reported by Device Manager.
    if (
        topic == "laptop"
        and context.get_subtopic() == "charging"
        and context.get_troubleshooting_step()
        == "waiting_for_battery_error_code"
    ):
        match = re.search(r"\b(?:code\s*)?(10|31|43)\b", text)

        if match:
            code = match.group(1)
            explanations = {
                "10": "Windows cannot start the battery device.",
                "31": "Windows cannot load the drivers needed for the device.",
                "43": "Windows stopped the device after it reported a problem.",
            }
            context.set_troubleshooting_step("checking_hardware_rescan")
            return (
                f"Device Manager Code {code}, sugar: "
                f"{explanations[code]} That doesn't prove the battery "
                "itself has failed. In Device Manager, select Action, "
                "then Scan for hardware changes. Does the battery "
                "device appear normally afterward?"
            )

        if re.search(r"\b(?:code\s*)?\d+\b", text):
            context.set_troubleshooting_step("waiting_for_laptop_model")
            return (
                "Thanks, darling. I don't have a verified explanation "
                "for that specific Device Manager code yet. "
                "What's your laptop's manufacturer and exact model "
                "so we can narrow down the next steps?"
            )

        return (
            "What's the exact numeric error code shown in Device "
            "Manager, sugar? For example: Code 10, Code 31, or Code 43."
        )

    # Handle the result of scanning for hardware changes.
    if (
        topic == "laptop"
        and context.get_subtopic() == "charging"
        and context.get_troubleshooting_step()
        == "checking_hardware_rescan"
    ):
        answer = re.sub(r"\s+", " ", text.replace(",", " ")).strip()

        if answer in (
            "yes", "yes it does", "yes it did",
            "yes it appeared", "yes it shows up",
            "the battery appeared", "battery appeared",
            "it's listed now", "it is listed now",
            "the battery is detected now",
        ):
            context.set_troubleshooting_step(
                "checking_battery_device_status"
            )
            return (
                "Good, sugar! Windows can see the battery device "
                "after the scan. Open its Properties window in "
                "Device Manager and check Device status. Does it "
                "say the device is working properly, or does it "
                "show an error code?"
            )

        if answer in (
            "no", "no it doesn't", "no it didn't",
            "still missing", "it's still missing",
            "it is still missing", "battery still missing",
            "the battery is still missing",
            "it didn't appear", "it did not appear",
            "no change",
        ):
            context.set_troubleshooting_step("waiting_for_laptop_model")
            return (
                "Alright, darling. The battery still isn't "
                "appearing after the hardware scan. That doesn't "
                "necessarily mean the battery has failed. "
                "What's your laptop's manufacturer and exact "
                "model? We can use that to identify the "
                "appropriate manufacturer diagnostics."
            )

        return (
            "After you selected Scan for hardware changes, "
            "did the battery appear in Device Manager, sugar?"
        )

    # Handle Windows battery device status results.
    if (
        topic == "laptop"
        and context.get_subtopic() == "charging"
        and context.get_troubleshooting_step()
        == "checking_battery_device_status"
    ):
        answer = re.sub(r"\s+", " ", text.replace(",", " ")).strip()

        if answer in (
            "working properly",
            "the device is working properly",
            "it says the device is working properly",
            "it is working properly",
            "no error",
            "no error code",
        ):
            context.set_troubleshooting_step("checking_battery_report")
            return (
                "Good news, sugar. Windows reports that the "
                "battery device is working properly, but that "
                "doesn't necessarily mean the battery itself "
                "is healthy. Let's check its condition. "
                "Have you generated a Windows battery report before?"
            )

        if answer in (
            "error code",
            "it shows an error code",
            "there is an error code",
            "it has an error code",
            "device error",
        ):
            context.set_troubleshooting_step("waiting_for_battery_error_code")
            return (
                "Alright, darling. That error code could help "
                "us identify what's wrong. What exact error "
                "code does Device Manager show in the battery "
                "device's Properties window?"
            )

    # Handle Device Manager battery detection results.
    if (
        topic == "laptop"
        and context.get_subtopic() == "charging"
        and context.get_troubleshooting_step()
        == "checking_device_manager_battery"
    ):
        answer = re.sub(r"\s+", " ", text.replace(",", " ")).strip()

        if answer in (
            "yes", "yes it is", "yes it does",
            "battery listed", "battery device listed",
            "it's listed", "it is listed",
            "i see the battery", "the battery is listed",
        ):
            context.set_troubleshooting_step("checking_battery_device_status")
            return (
                "Good, sugar. Windows can see a battery device "
                "in Device Manager. Open its Properties window "
                "and check Device status. Does it say the device "
                "is working properly, or does it show an error code?"
            )

        if answer in (
            "no", "no it isn't", "no it doesn't",
            "batteries section missing", "section missing",
            "the batteries section is missing",
            "no batteries section", "it's missing",
            "it is missing",
        ):
            context.set_troubleshooting_step("checking_hardware_rescan")
            return (
                "Alright, darling. In Device Manager, select "
                "Action, then Scan for hardware changes. "
                "If the Batteries section still doesn't appear, "
                "we may need your laptop manufacturer's hardware "
                "diagnostics. Does the battery appear after "
                "the scan?"
            )

    # Handle manufacturer diagnostic error-code details.
    if (
        topic == "laptop"
        and context.get_subtopic() == "charging"
        and context.get_troubleshooting_step()
        == "waiting_for_manufacturer_error_code"
    ):
        answer = re.sub(r"\s+", " ", text).strip()

        code_match = re.search(
            r"\b[0-9]{2,}(?:-[0-9a-z]+)*\b",
            answer,
        )

        manufacturer_match = re.search(
            r"\b(dell|lenovo|hp|asus|acer)\b",
            answer,
        )

        if not code_match:
            saved_code = context.diagnostic_details.get("error_code")
            if saved_code and manufacturer_match:
                code = saved_code
                manufacturer = manufacturer_match.group(1).upper()

                context.diagnostic_details.clear()
                context.clear_troubleshooting_step()

                return (
                    f"Thanks, sugar. You reported diagnostic code {code} "
                    f"from a {manufacturer} laptop. I can't confirm "
                    "the meaning of that code without the manufacturer's "
                    "official documentation and the full diagnostic "
                    "message. Save the result and check the manufacturer's "
                    "support resources for your exact laptop model. "
                    "Don't replace hardware based on the code alone."
                )

            if manufacturer_match:
                context.diagnostic_details["manufacturer"] = (
                    manufacturer_match.group(1).upper()
                )

            return (
                "I still need the exact diagnostic error code, "
                "sugar. Please copy the code and its accompanying "
                "message exactly as the diagnostic displayed them."
            )

        if not manufacturer_match:
            saved_manufacturer = context.diagnostic_details.get(
                "manufacturer"
            )

            if saved_manufacturer:
                code = code_match.group(0)
                manufacturer = saved_manufacturer

                context.diagnostic_details.clear()
                context.clear_troubleshooting_step()

                return (
                    f"Thanks, sugar. You reported diagnostic code {code} "
                    f"from a {manufacturer} laptop. I can't confirm "
                    "the meaning of that code without the manufacturer's "
                    "official documentation and the full diagnostic "
                    "message. Save the result and check the manufacturer's "
                    "support resources for your exact laptop model. "
                    "Don't replace hardware based on the code alone."
                )

            code = code_match.group(0)
            if code.lower().startswith("code "):
                code = code[5:]

            context.diagnostic_details["error_code"] = code

            return (
                "I've got the diagnostic code, darling. "
                "Which laptop manufacturer reported it: "
                "Dell, Lenovo, HP, ASUS, or Acer? "
                "Please include the diagnostic message too."
            )

        code = code_match.group(0)
        if code.lower().startswith("code "):
            code = code[5:]
        manufacturer = manufacturer_match.group(1).upper()

        context.clear_troubleshooting_step()

        return (
            f"Thanks, sugar. You reported diagnostic code {code} "
            f"from a {manufacturer} laptop. I can't confirm "
            "the meaning of that code without the manufacturer's "
            "official documentation and the full diagnostic "
            "message. Save the result and check the manufacturer's "
            "support resources for your exact laptop model. "
            "Don't replace hardware based on the code alone."
        )

    # Handle manufacturer battery diagnostic results.
    if (
        topic == "laptop"
        and context.get_subtopic() == "charging"
        and context.get_troubleshooting_step()
        == "waiting_for_manufacturer_diagnostics"
    ):
        answer = re.sub(r"\s+", " ", text).strip()

        if re.search(
            r"\b(error|fault|code)\b|\b[0-9]{3,}\b",
            answer,
        ):
            context.set_troubleshooting_step(
                "waiting_for_manufacturer_error_code"
            )
            return (
                "Gotcha, sugar. Please tell me the exact diagnostic "
                "error code and message, along with your laptop's "
                "manufacturer. I don't want to guess what the "
                "result means."
            )

        if re.search(
            r"\b(failed|failure|fail|didn't pass|did not pass)\b",
            answer,
        ):
            context.clear_troubleshooting_step()
            return (
                "That diagnostic reported a failure, sugar. "
                "Save the exact result and any reference number. "
                "Check your manufacturer's official support "
                "resources before deciding whether the battery "
                "or another component needs replacement. "
                "If the battery is swollen, stop using or "
                "charging the laptop."
            )

        if re.search(
            r"\b(passed|pass|no issues|no problems)\b",
            answer,
        ):
            context.clear_troubleshooting_step()
            return (
                "Good to know, sugar! The diagnostic didn't "
                "report a problem, but that doesn't completely "
                "rule out a charging issue. The charger, "
                "charging port, firmware, or battery settings "
                "may still need checking."
            )

        return (
            "Tell me what the diagnostic reported, darling. "
            "Did the battery test pass, fail, or show an "
            "error code?"
        )

    # Handle laptop manufacturer and model information.
    if (
        topic == "laptop"
        and context.get_subtopic() == "charging"
        and context.get_troubleshooting_step()
        == "waiting_for_laptop_model"
    ):
        answer = re.sub(r"\s+", " ", text).strip()

        manufacturers = {
            "dell": (
                "Dell",
                "Dell SupportAssist or Dell's official hardware "
                "diagnostics"
            ),
            "lenovo": (
                "Lenovo",
                "Lenovo Vantage or Lenovo Diagnostics"
            ),
            "hp": (
                "HP",
                "HP PC Hardware Diagnostics"
            ),
            "asus": (
                "ASUS",
                "MyASUS or ASUS System Diagnosis"
            ),
            "acer": (
                "Acer",
                "Acer Care Center"
            ),
        }

        for keyword, (manufacturer, diagnostic) in manufacturers.items():
            if re.search(r"\b" + re.escape(keyword) + r"\b", answer):
                context.set_troubleshooting_step("waiting_for_manufacturer_diagnostics")
                article = "an" if manufacturer in ("HP", "ASUS", "Acer") else "a"
                return (
                    f"Got it, sugar! You're using {article} {manufacturer} "
                    f"laptop. For battery troubleshooting, check "
                    f"{diagnostic}. The available tests depend on "
                    "your exact model. Run the battery or power "
                    "diagnostic if one is offered, and tell me "
                    "what result it reports."
                )

        return (
            "Thanks, darling. I haven't identified a supported "
            "manufacturer from that answer yet. Please give me "
            "the laptop's manufacturer and exact model, such "
            "as Dell Latitude 5420 or Lenovo ThinkPad T480."
        )

    # Handle Windows battery detection troubleshooting.
    if (
        topic == "laptop"
        and context.get_subtopic() == "charging"
        and context.get_troubleshooting_step()
        == "checking_battery_detection"
    ):
        answer = re.sub(r"\s+", " ", text.replace(",", " ")).strip()

        if answer in (
            "yes", "yes it does", "yes it detects it",
            "windows detects it", "it detects normally",
            "it detects the battery", "detected normally",
            "the battery is detected",
        ):
            context.set_troubleshooting_step("waiting_for_laptop_model")
            return (
                "Good, sugar. Windows can see the battery, "
                "so let's narrow down why it isn't charging "
                "properly. What's your laptop's manufacturer "
                "and model number?"
            )

        if answer in (
            "no", "no it doesn't", "no it does not",
            "battery not detected", "battery missing",
            "not detected", "windows doesn't detect it",
            "windows does not detect it",
        ):
            context.set_troubleshooting_step("checking_device_manager_battery")
            return (
                "Alright, darling. If Windows isn't detecting "
                "the battery, restart your laptop first. "
                "Then open Device Manager and look under "
                "Batteries. Do you see a battery device listed "
                "there, or is the Batteries section missing?"
            )

    # Handle answers about battery charge-limit settings.
    if (
        topic == "laptop"
        and context.get_subtopic() == "charging"
        and context.get_troubleshooting_step()
        == "checking_battery_health_setting"
    ):
        answer = re.sub(r"\s+", " ", text.replace(",", " ")).strip()

        if answer in (
            "yes", "yes it is", "yes it's on",
            "yes it is enabled", "it's enabled",
            "the setting is on",
        ):
            context.clear_troubleshooting_step()
            return (
                "There we go, sugar! If your battery charge limit "
                "is enabled, that likely explains why charging "
                "stops around 80 percent. It's a battery health "
                "feature, not necessarily a fault. If you want "
                "to change the limit, I can help you find the "
                "setting for your laptop model."
            )

        if answer in (
            "no", "no it isn't", "no it's off",
            "no it is disabled", "it's disabled",
            "the setting is off",
        ):
            context.set_troubleshooting_step("checking_battery_detection")
            return (
                "Alright, darling. If charge limiting is off, "
                "we should investigate further. Does Windows "
                "detect your battery normally, or does it show "
                "a battery missing or not detected message?"
            )

    # Handle battery charge-limit troubleshooting.
    if (
        topic == "laptop"
        and context.get_subtopic() == "charging"
        and context.get_troubleshooting_step()
        == "checking_charge_limit"
    ):
        answer = re.sub(r"\s+", " ", text.replace(",", " ")).strip()

        if answer in (
            "80", "80%", "80 percent",
            "it's stuck at 80%", "it's stuck at 80 percent",
            "it stays at 80%", "it stays at 80 percent",
            "around 80%", "around 80 percent",
        ):
            context.set_troubleshooting_step("checking_battery_health_setting")
            return (
                "Some laptops intentionally stop charging around "
                "80 percent to protect battery health, sugar. "
                "Check your manufacturer's battery health or "
                "charging settings to see whether a charge limit "
                "is enabled. Is that setting turned on?"
            )

    # Handle answers about laptop charging warnings.
    if (
        topic == "laptop"
        and context.get_subtopic() == "charging"
        and context.get_troubleshooting_step()
        == "checking_charging_warning"
    ):
        answer = re.sub(r"\s+", " ", text.replace(",", " ")).strip()

        if answer in (
            "yes", "yes i am", "yes it does",
            "yes there's a warning", "yes there is a warning",
        ):
            context.set_troubleshooting_step("waiting_for_charging_warning")
            return (
                "Alright, sugar. What exactly does the charging "
                "warning say? Give me the message as it appears "
                "on your laptop."
            )

        if answer in (
            "no", "no i'm not", "no it doesn't",
            "no there isn't", "no warning",
        ):
            context.set_troubleshooting_step("checking_charge_limit")
            return (
                "Gotcha, darling. Some laptops have a battery "
                "charge limit that stops charging at a certain "
                "percentage. Is your battery staying around "
                "80 percent, or is it stuck at a different level?"
            )

    # Handle answers about the original laptop charger.
    if (
        topic == "laptop"
        and context.get_subtopic() == "charging"
        and context.get_troubleshooting_step()
        == "checking_original_charger"
    ):
        answer = re.sub(r"\s+", " ", text.replace(",", " ")).strip()

        if answer in (
            "yes", "yes i am", "yes it's the original",
            "yes it is", "i'm using the original charger",
        ):
            context.set_troubleshooting_step("checking_charging_warning")
            return (
                "Alright, sugar! Since you're using the original "
                "charger, let's narrow this down. Does your laptop "
                "show any charging error or battery warning?"
            )

        if answer in (
            "no", "no i'm not", "no i am not",
            "no it's a replacement", "i'm using a replacement",
        ):
            context.clear_troubleshooting_step()
            return (
                "Gotcha, darling. A replacement charger might not "
                "supply the power your laptop needs. Check that its "
                "wattage, voltage, and connector match your laptop's "
                "requirements. What's your laptop's model number?"
            )

    # Context-aware follow-ups for everyday topics.
    if (
        topic == "laptop"
        and context.get_subtopic() == "charging"
        and context.get_troubleshooting_step()
        == "checking_charger_connection"
    ):
        answer = re.sub(r"\s+", " ", text.replace(",", " ")).strip()
        if answer in (
            "yes but the battery percentage isn't increasing",
            "yes but the battery percentage is not increasing",
            "yes but it's not charging",
            "yes but it is not charging",
        ):
            context.set_troubleshooting_step("checking_original_charger")
            return (
                "Gotcha, sugar! Your laptop detects the charger, "
                "but the battery percentage isn't increasing. "
                "Let's check whether the charger supplies enough "
                "power. Are you using the original charger?"
            )

    if topic == "laptop" and context.get_subtopic() == "charging":
        if text in ("it's not charging", "it is not charging"):
            context.set_troubleshooting_step("checking_charger_connection")
            return (
                "If your laptop isn't charging, sugar, "
                "first check the power outlet, charger, "
                "and charging connection. "
                "Does the laptop show that it's plugged in?"
            )

        if text in ("it's charging slowly", "it is charging slowly"):
            return (
                "Slow charging can happen when the charger "
                "doesn't supply enough power, darling. "
                "Are you using the original charger "
                "that came with your laptop?"
            )

        if text in (
            "it loses power while plugged in",
            "it's losing power while plugged in",
        ):
            return (
                "If your laptop loses battery power while "
                "plugged in, sugar, the charger might not "
                "be supplying enough power. "
                "Does this happen during gaming or heavy use, "
                "or even when the laptop is idle?"
            )

    if topic == "laptop" and context.get_subtopic() == "battery_replacement":
        if text in (
            "find a compatible battery",
            "find a replacement battery",
        ):
            return (
                "I can help you figure out which battery fits, "
                "sugar! What's your laptop's manufacturer "
                "and exact model number? We'll need those "
                "before identifying a compatible replacement."
            )

        if text in (
            "does it need replacing",
            "does the battery need replacing",
        ):
            return (
                "A worn-out laptop battery may drain quickly, "
                "shut down unexpectedly, or stop holding a "
                "charge, darling. Is yours showing any of "
                "those symptoms? If the battery is swollen, "
                "stop using or charging it."
            )

    if topic == "laptop":
        if text in ("charging", "charging it"):
            context.set_subtopic("charging")
            return (
                "Is your laptop charging slowly, not charging "
                "at all, or losing power while plugged in, sugar?"
            )

        if text in (
            "replacing it",
            "battery replacement",
            "replacing the battery",
        ):
            context.set_subtopic("battery_replacement")
            return (
                "Are you looking for a compatible replacement "
                "battery, or trying to determine whether your "
                "current battery needs replacing, darling?"
            )

        if text in ("battery life", "the battery life"):
            context.set_subtopic("battery_life")
            return (
                "Gotcha, sugar! Are you having trouble "
                "with how long your laptop lasts between charges?"
            )

        if (
            context.get_subtopic() == "battery_life"
            and text in (
                "how can i improve it",
                "how do i improve it",
                "how can i make it last longer",
            )
        ):
            return (
                "To improve your laptop's battery life, sugar, "
                "try lowering screen brightness, using battery "
                "saver mode, and closing unnecessary background "
                "applications."
            )

        if re.fullmatch(r"(?:and )?(?:what about (?:its|the) battery|how['’]s its battery|tell me about its battery)", text):
            return (
                "Your laptop's battery, sugar? "
                "Are we looking at battery life, charging, "
                "or replacing it?"
            )

    if topic == "car":
        if re.fullmatch(r"(?:and )?(?:what about (?:the|its) wheels|how about the tires)", text):
            return (
                "Your car's wheels, darling? "
                "Are you thinking about tires, wheel sizes, "
                "or something else?"
            )

        if re.fullmatch(r"(?:and )?(?:its engine|tell me about its engine)", text):
            return (
                "What would you like to know about "
                "your car's engine, sugar?"
            )

    return None
