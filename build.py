"""WiCal 공개 문서 사이트 생성. 미확정 운영정보는 공개 빌드에서 허용하지 않는다."""
from pathlib import Path
from html import escape
from urllib.parse import quote
import argparse
import json
import re
import shutil

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--preview', action='store_true', help='로컬 검토용 초안 생성')
parser.add_argument('--output', choices=('_site', 'docs'), default='_site', help='생성 위치. GitHub Pages 배포는 docs 사용')
args = parser.parse_args()
if args.preview and args.output == 'docs':
    raise SystemExit('배포 폴더에는 초안을 생성할 수 없습니다. --preview는 기본 _site 폴더를 사용하세요.')
config = json.loads((ROOT / 'site.json').read_text())
copy = json.loads((ROOT / 'content.json').read_text())
if not args.preview:
    for key in ('operator', 'email', 'effective_date', 'support_retention'):
        if not config.get(key):
            raise SystemExit(f'공개 빌드 중단: site.json의 {key} 확인 필요')
    if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', config['email']):
        raise SystemExit('공개 빌드 중단: 문의 이메일 형식 확인 필요')
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', config['effective_date']):
        raise SystemExit('공개 빌드 중단: 시행일은 YYYY-MM-DD 형식이어야 함')
    retention = config['support_retention']
    if not isinstance(retention, dict) or any(not isinstance(retention.get(locale), str) or not retention[locale].strip() for locale in ('ko', 'en')):
        raise SystemExit('공개 빌드 중단: 문의 메일 보관 기준의 한국어·영어 문구 확인 필요')
out = ROOT / args.output
if out.exists():
    shutil.rmtree(out)
out.mkdir()
shutil.copytree(ROOT / 'assets', out / 'assets')
(out / '.nojekyll').touch()
base = config['base_url'].rstrip('/')
prefix = '/' + base.split('/', 3)[3].strip('/') if len(base.split('/', 3)) > 3 else ''
operator = escape(config.get('operator') or '운영자 정보 확인 중 / Operator pending')
email = escape(config.get('email') or '')
date = escape(config.get('effective_date') or '게시 전 확인 / Pending publication')

def href(path):
    return prefix + '/' + path.lstrip('/')

def contact(locale, button=True):
    if not email:
        return '<p class="note">문의 이메일 확인 후 게시합니다. / Contact details are pending.</p>'
    label = copy[locale]['contact_button']
    target = 'mailto:' + email + '?subject=' + quote('WiCal Support' if locale == 'en' else 'WiCal 문의')
    return f'<a class="button" href="{target}">{label} <span aria-hidden="true">↗</span></a><a class="email" href="mailto:{email}">{email}</a>' if button else f'<a href="mailto:{email}">{email}</a>'

def interpolate(text, locale):
    retention = (config.get('support_retention') or {}).get(locale) or '문의 메일 보관 기준 확인 중 / Email retention pending.'
    return text.replace('{operator}', operator).replace('{email}', contact(locale, False)).replace('{date}', date).replace('{support}', href(f'{locale}/support/')).replace('{privacy}', href(f'{locale}/privacy/')).replace('{support_retention}', escape(retention))

def layout(locale, kind, title, description, body):
    c = copy[locale]
    path = f'{locale}/' + (f'{kind}/' if kind else '')
    other = 'en' if locale == 'ko' else 'ko'
    other_path = f'{other}/' + (f'{kind}/' if kind else '')
    active_support = ' aria-current="page"' if kind == 'support' else ''
    active_privacy = ' aria-current="page"' if kind == 'privacy' else ''
    draft = '<div class="draft">게시 전 검토용 초안 · Local preview only</div>' if args.preview else ''
    robots = '<meta name="robots" content="noindex,nofollow">' if args.preview else ''
    return f'''<!doctype html>
<html lang="{locale}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)} · WiCal</title><meta name="description" content="{escape(description)}">{robots}
<meta name="theme-color" content="#f6f7f3"><link rel="icon" type="image/png" href="{href('assets/app-icon.png')}">
<link rel="canonical" href="{base}/{path}"><link rel="alternate" hreflang="{other}" href="{base}/{other_path}">
<link rel="stylesheet" href="{href('assets/style.css')}"></head><body>
<a class="skip" href="#main">{c['skip']}</a>{draft}
<header><div class="shell header-inner"><a class="brand" href="{href(locale+'/')}"><img src="{href('assets/app-icon.png')}" alt="" width="44" height="44">WiCal</a>
<nav aria-label="{c['navigation']}"><a href="{href(locale+'/support/')}"{active_support}>{c['support_label']}</a><a href="{href(locale+'/privacy/')}"{active_privacy}>{c['privacy_label']}</a><a class="language" href="{href(other_path)}" lang="{other}" hreflang="{other}">{'English' if locale=='ko' else '한국어'}</a></nav></div></header>
<main id="main" class="shell">{body}</main>
<footer><div class="shell footer-inner"><span>WiCal · {operator}</span><div class="footer-links"><a href="{href(locale+'/support/')}">{c['support_label']}</a><a href="{href(locale+'/privacy/')}">{c['privacy_label']}</a></div></div></footer>
</body></html>'''

def write(path, content):
    target = out / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding='utf-8')

for locale, c in copy.items():
    hero = lambda eyebrow, title, lead: f'<div class="hero"><p class="eyebrow">{eyebrow}</p><h1>{title}</h1><p class="lead">{lead}</p></div>'
    home = hero('YOUR CALENDAR, WITHIN VIEW', c['home_title'], c['home_lead'])
    home += '<div class="home-links">'
    for number, kind in enumerate(('support', 'privacy'), 1):
        home += f'<section class="card"><div class="card-number">0{number}</div><h2>{c[kind+"_label"]}</h2><p>{c[kind+"_summary"]}</p><a class="button secondary" href="{href(locale+"/"+kind+"/")}">{c["read_more"]} <span aria-hidden="true">↗</span></a></section>'
    home += '</div>'
    write(f'{locale}/index.html', layout(locale, '', c['home_title'], c['home_lead'], home))
    support = hero('WICAL SUPPORT', c['support_title'], c['support_lead'])
    support += f'<div class="intro-grid"><section class="card contact-card"><div class="card-number">01 / CONTACT</div><h2>{c["contact_title"]}</h2><p>{c["contact_intro"]}</p>{contact(locale)}</section><section class="card"><div class="card-number">02 / BEFORE YOU WRITE</div><h2>{c["report_title"]}</h2><p>{c["report_intro"]}</p><p class="note">{c["report_privacy"]}</p></section></div>'
    support += f'<section class="faq" aria-labelledby="faq-title"><h2 id="faq-title">{c["faq_title"]}</h2>'
    for item in c['faq']:
        support += f'<details><summary>{item["question"]}</summary><div class="answer">{interpolate(item["answer"],locale)}</div></details>'
    support += '</section>'
    write(f'{locale}/support/index.html', layout(locale, 'support', c['support_label'], c['support_lead'], support))
    privacy = hero('WICAL PRIVACY', c['privacy_label'], c['privacy_lead'])
    privacy += f'<div class="meta"><span>{c["effective_label"]}: {date}</span><span>{c["operator_label"]}: {operator}</span></div><div class="legal-grid"><aside class="toc" aria-label="{c["contents_label"]}"><ol>'
    for section in c['privacy_sections']:
        privacy += f'<li><a href="#{section["id"]}">{section["title"]}</a></li>'
    privacy += '</ol></aside><article class="legal">'
    for section in c['privacy_sections']:
        privacy += f'<section id="{section["id"]}"><h2>{section["title"]}</h2>{interpolate(section["body"],locale)}</section>'
    privacy += '</article></div>'
    write(f'{locale}/privacy/index.html', layout(locale, 'privacy', c['privacy_label'], c['privacy_lead'], privacy))
root_body = '<div class="hero"><p class="eyebrow">WICAL HELP CENTER</p><h1>매일의 일정, 더 가까이.<br>Your calendar, within view.</h1><p class="lead">WiCal 지원 및 개인정보 안내 · Support and privacy information</p></div>'
root_body += f'<div class="language-picker"><a class="button" href="{href("ko/")}" lang="ko">한국어</a><a class="button secondary" href="{href("en/")}" lang="en">English</a></div>'
write('index.html', layout('ko', '', 'WiCal 도움말 / Help Center', 'WiCal 지원 및 개인정보 안내', root_body).replace(f'<link rel="canonical" href="{base}/ko/">', f'<link rel="canonical" href="{base}/">'))
write('404.html', layout('ko', '', '페이지를 찾을 수 없습니다 / Page not found', 'WiCal', f'<div class="hero"><p class="eyebrow">404</p><h1>페이지를 찾을 수 없습니다.</h1><p class="lead">Page not found.</p></div><p><a class="button" href="{href("")}">WiCal 도움말 / Help Center</a></p>'))
write('robots.txt', 'User-agent: *\n' + ('Disallow: /\n' if args.preview else f'Allow: /\nSitemap: {base}/sitemap.xml\n'))
paths = [''] + [f'{locale}/{kind}' for locale in copy for kind in ('','support/','privacy/')]
write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{base}/{path}</loc></url>' for path in paths) + '</urlset>')
print(f'{len(paths)}개 페이지 생성 완료: {out} (preview={args.preview})')

# The same source repository also owns the existing Sites publisher deployment.
# A local draft must never overwrite its public build output.
if not args.preview:
    publisher_out = ROOT / 'dist'
    if publisher_out.exists():
        shutil.rmtree(publisher_out)
    shutil.copytree(ROOT / 'publisher', publisher_out)
    publisher_home = (publisher_out / 'index.html').read_text(encoding='utf-8')
    for token, value in {'support_base_url': escape(base, quote=True),
                         'operator': operator, 'email': email}.items():
        publisher_home = publisher_home.replace('{{' + token + '}}', value)
    if '{{' in publisher_home:
        raise SystemExit('대표 페이지에 치환되지 않은 항목이 있습니다.')
    (publisher_out / 'index.html').write_text(publisher_home, encoding='utf-8')
    print(f'대표 페이지·광고 인증 파일 생성 완료: {publisher_out}')
