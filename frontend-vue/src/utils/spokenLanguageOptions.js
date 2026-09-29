export function spokenLanguageSelectOptions(catalog = []) {
  return (catalog || [])
    .filter((item) => item?.name)
    .map((item) => ({
      value: item.name,
      label: item.name,
      aliases: Array.isArray(item.aliases) ? item.aliases : [],
    }))
}
