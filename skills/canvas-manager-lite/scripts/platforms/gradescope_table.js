// Gradescope course page (https://www.gradescope.com/courses/{id}): read the
// student assignment table. Run with `opencli browser <session> eval`.
JSON.stringify({url:location.href, rows:[...document.querySelectorAll('#assignments-student-table tbody tr')].map(tr=>{
  const th=tr.querySelector('th'); const a=th&&th.querySelector('a,button');
  const tds=[...tr.querySelectorAll('td')];
  const times=[...tr.querySelectorAll('time')].map(t=>({dt:t.getAttribute('datetime'),txt:t.innerText,cls:t.className, lab:t.getAttribute('aria-label')}));
  return {name:th?th.innerText.trim():'', href:a?(a.getAttribute('href')||a.getAttribute('data-post-url')):null, status:tds[0]?tds[0].innerText.trim():'', times};
})})
