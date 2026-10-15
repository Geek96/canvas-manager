// Canvas REST dump for one course, run inside the logged-in Canvas tab via
// `opencli browser <session> eval`. __COURSE__ is replaced with the course id.
// Returns JSON: course (+syllabus), assignments (+submission), assignment groups,
// announcements, discussions, modules (+items), quizzes, pages (+module pages,
// front page and pages linked from it).
(async () => {
  const C = __COURSE__;
  const H = { headers: { Accept: 'application/json' } };
  async function all(url) {
    let out = [], next = url, status = 200;
    while (next) {
      const r = await fetch(next, H);
      status = r.status;
      if (!r.ok) return { error: r.status, items: out };
      const j = await r.json();
      if (Array.isArray(j)) out = out.concat(j); else return j;
      const link = r.headers.get('Link') || '';
      const m = link.split(',').find(s => s.includes('rel="next"'));
      next = m ? m.match(/<([^>]+)>/)[1] : null;
    }
    return out;
  }
  const res = {};
  res.course = await all(`/api/v1/courses/${C}?include[]=syllabus_body&include[]=term`);
  res.assignments = await all(`/api/v1/courses/${C}/assignments?per_page=100&include[]=submission`);
  res.groups = await all(`/api/v1/courses/${C}/assignment_groups?per_page=100`);
  res.announcements = await all(`/api/v1/courses/${C}/discussion_topics?only_announcements=true&per_page=100`);
  res.discussions = await all(`/api/v1/courses/${C}/discussion_topics?per_page=100`);
  res.modules = await all(`/api/v1/courses/${C}/modules?include[]=items&per_page=100`);
  res.quizzes = await all(`/api/v1/courses/${C}/quizzes?per_page=100`);
  const modOf = {};
  const want = [];
  if (Array.isArray(res.modules)) for (const m of res.modules) for (const i of (m.items||[])) if (i.type==='Page' && i.page_url) { modOf[i.page_url]=m.id; want.push(i.page_url); }
  let pages = await all(`/api/v1/courses/${C}/pages?per_page=100`);
  res.pages_list_error = Array.isArray(pages) ? null : pages.error;
  const urls = Array.isArray(pages) ? pages.map(p=>p.url) : [];
  res.front_page = await all(`/api/v1/courses/${C}/front_page`);
  const fpb = (res.front_page && res.front_page.body ? res.front_page.body : '') + (res.course && res.course.syllabus_body ? res.course.syllabus_body : '');
  if (res.front_page && res.front_page.url) want.push(res.front_page.url);
  for (const m of fpb.matchAll(new RegExp(`/courses/${C}/pages/([\\w%.-]+)`, 'g'))) want.push(decodeURIComponent(m[1]));
  for (const u of want) if (!urls.includes(u)) urls.push(u);
  res.pages = [];
  for (const u of urls) {
    const full = await all(`/api/v1/courses/${C}/pages/${encodeURIComponent(u)}`);
    if (full && full.body !== undefined) { full._module = modOf[u] || null; res.pages.push(full); }
  }
  return JSON.stringify(res);
})()
