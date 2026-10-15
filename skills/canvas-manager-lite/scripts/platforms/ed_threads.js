// Ed Discussion threads for one course via the Ed API, using the token Ed keeps
// in localStorage of the logged-in tab. __ED__ is replaced with the Ed course id.
// Uses the US region host (us.edstem.org); courses on another region need that host instead.
(async()=>{const tok=localStorage.getItem('authToken');const H={headers:{'x-token':tok}};let all=[];
for(let off=0;off<1000;off+=100){const r=await fetch('https://us.edstem.org/api/courses/__ED__/threads?limit=100&sort=new&offset='+off,H);if(!r.ok)return JSON.stringify({err:r.status});const j=await r.json();
all=all.concat(j.threads.map(t=>({id:t.id,number:t.number,title:t.title,type:t.type,cat:t.category,sub:t.subcategory,pinned:t.is_pinned,role:t.user?t.user.course_role:null,author:t.user?t.user.name:null,created:t.created_at,doc:t.document})));if(j.threads.length<100)break;}
return JSON.stringify(all)})()
