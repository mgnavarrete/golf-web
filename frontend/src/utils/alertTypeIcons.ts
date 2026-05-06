import phoneIcon from "@/assets/images/alerts/phone.svg";
import helmetIcon from "@/assets/images/alerts/helmet.svg";
import safetyVestIcon from "@/assets/images/alerts/safety-vest.svg";
import personIcon from "@/assets/images/alerts/person.svg";
import restrictedAreaIcon from "@/assets/images/alerts/restricted-area.svg";

const alertTypeIcons: Record<string, string> = {
  CELLPHONE: phoneIcon,
  PHONE: phoneIcon,
  EPP_HELMET: helmetIcon,
  EPP_VEST: safetyVestIcon,
  PERSON: personIcon,
  RESTRICTED_AREA: restrictedAreaIcon,
};

export function getAlertTypeIconPath(alertType: string): string | null {
  return alertTypeIcons[alertType] ?? null;
}

