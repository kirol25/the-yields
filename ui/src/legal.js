import { APP_NAME } from "./config.js";

export const LEGAL = {
  appName: APP_NAME,
  operatorName: "[Project Maintainer]",
  street: "[Street Address]",
  postalCode: "24106",
  city: "Kiel",
  country: "Deutschland",
  email: "contact@the-yields.com",
  phone: "",
  vatId: "",
  commercialRegister: "",
  responsibleForContent: "[Project Maintainer]",
  lastUpdatedIso: "2026-03-08",
  lastUpdatedDe: "8. Maerz 2026",
  lastUpdatedEn: "March 8, 2026",
};

const REQUIRED_FIELDS = [
  {
    key: "street",
    labelDe: "Strasse und Hausnummer",
    labelEn: "Street and house number",
  },
  {
    key: "postalCode",
    labelDe: "Postleitzahl",
    labelEn: "Postal code",
  },
  {
    key: "city",
    labelDe: "Ort",
    labelEn: "City",
  },
];

export function getMissingLegalFields(locale = "de") {
  const useGerman = locale === "de";
  return REQUIRED_FIELDS.filter(
    ({ key }) => !String(LEGAL[key] || "").trim(),
  ).map(({ labelDe, labelEn }) => (useGerman ? labelDe : labelEn));
}

export function getLegalAddress(locale = "de") {
  const useGerman = locale === "de";
  return {
    street:
      LEGAL.street ||
      (useGerman ? "[Strasse und Hausnummer]" : "[Street and house number]"),
    cityLine:
      LEGAL.postalCode && LEGAL.city
        ? `${LEGAL.postalCode} ${LEGAL.city}`
        : useGerman
          ? "[PLZ] [Ort]"
          : "[Postal code] [City]",
    country: LEGAL.country || (useGerman ? "Deutschland" : "Germany"),
  };
}
