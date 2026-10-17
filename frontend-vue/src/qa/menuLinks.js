/** Tester menu entries; triagers also get the triage page. */
export function testerMenuLinks(qa) {
  const links = [
    { name: 'TesterHub', icon: 'bi-speedometer2', label: 'qa.menu.hub' },
    { name: 'TesterAccounts', icon: 'bi-people', label: 'qa.menu.accounts' },
    { name: 'TesterChecklist', icon: 'bi-ui-checks', label: 'qa.menu.checklist' },
    { name: 'TesterReports', icon: 'bi-list-check', label: 'qa.menu.myReports' },
    { name: 'TesterOutbox', icon: 'bi-envelope', label: 'qa.menu.outbox' },
    { name: 'TesterGuide', icon: 'bi-journal-text', label: 'qa.menu.guide' },
  ]
  if (qa?.isTriager) links.splice(1, 0, { name: 'QaTriage', icon: 'bi-kanban', label: 'qa.menu.triage' })
  return links
}
