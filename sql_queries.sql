select id
from linkedin.open_positions 
group by id 
having count(*) > 1;

delete from linkedin.open_positions l1 using(
	select min(ctid) ctid, id 
	from linkedin.open_positions l2 
	group by id 
	having count(*) > 1
) l2
where l1.id = l2.id 
	and l1.ctid > l2.ctid;
	

delete from linkedin.open_positions

select * from linkedin.open_positions
--where title ~* '(Full ?Stack)|(back ?end) Developer'
where title ~* 'traineeship|internship|intern|junior|trainee|docent|c\+\+|java|devops|developer'

select title, count(*) cnt from linkedin.open_positions
group by title order by count(*) desc

select * from linkedin.open_positions
where title ~* 'rust'



select * from linkedin.open_positions
where "location"  ~* 'Netherlands'
	and title !~* 'werken|werking|werkvoorbereider|beheerder|adviseur|inspecteur'

-- Netherlands 
	-- title stop words:
			-- 'werken', 'werking', 'beheerder', 'werkvoorbereider', 'adviseur', 'inspecteur', 'ontwerper',
			-- title !~* '[a-zA-Z0-9]' -- выкидываем иероглифы
	-- description stop words: 
			-- 'jij', 'werken', 'een'
	
	-- !!! description ~* 'have ' and description ~* ' you ' - Выборка всех англоязычных описаний вакансии


with subselect as (
	select title from linkedin.open_positions
	where not (description ~* 'have ' and description ~* ' you ')
),
dict as (
	select regexp_split_to_table(regexp_replace(regexp_replace(lower(title), '\,|\.|/|-|\)|\(|&|–', ' ', 'g'), '\s+', ' ', 'g'), '\s') as word 
	from subselect
)
select word, count(*) cnt
from dict
group by word
order by cnt desc;



	
-- Частотный анализ текста описаний

with dict as (
	select replace(replace(regexp_split_to_table(description, '\s'), ',', ''), '.', '') as word 
	from linkedin.open_positions
	where "location"  ~* 'Netherlands'
)
select word, count(*) cnt
from dict
group by word
order by cnt desc

select title, description  from linkedin.open_positions
where "location"  ~* 'Netherlands'
	-- and title ~* 'adviseur|inspecteur'
	and not (description ~* ' en '
	and description ~* ' de '
	and description ~* ' van '
	and description ~* ' je ')


	
select * from linkedin.open_positions
where 	title !~* 'å|ä|ü|ö|ø|é|koordinator|projekt|assistenz|landmeter|tiker|techniker|german\y|analist|techniek|\Yiker\y|Merchandiserentwickler|konsulent|udvikler|leider|\yen\y|\ytill\y|\Yteur\y|daten|beheer|landschap|ontwerper|ontwikkelaar|ondersteuner|transporten|rojekten|technische|industrie|planarkitekt|werker|geoteknikker|systemansvarlig|samordnare|analytiker|werkvoor|tekenaar|besiktningstekniker|\yopus\y|bilprovning|\yund\y|\yen\y|transportplanner|planoloog|stedenbouwkundige|erfaren|adviseur|\yoch\y|deutsche|geotekniker|breitband|werkstudent|\yog\y|bergen|dokumentation|\ydie\y|fachkraft|\yinom\y|\yals\y|bereich|\yvan\y|vermessungstechniker|netzdokumentation|\ymit\y|\ystrom\y|stavanger|geomatiker|netzplaner|trondheim|fachbereich|\yoder\y|stadterlebnisse|upplands|ecoloog|\yder\y|ingenieur|bij|softwareentwickler|zeichner|schwerpunkt|\ymet\y|bauzeichner|praktikum|fagarbeider|adviseur|entwicklung|\yals\y|technischer|konsult|spezialist|vermessungstechniker|informatiespecialist|informatie|stadterlebnisse|telekommunikation|landskapsarkitekt|ict'
	and title !~* 'traineeship|internship|intern|junior|\yjr\y|trainee|docent|phd|postdoc|doktorand|praktikant|archeoloog|resource\splanner|merchandiser|staff|geotechnical|\yhr\y|Dokument|lawyer|backend|frontend|r&d|part\-time|software engineer|director|hydr[oa]|\yux\y|test|full[\s-]?stack|devops|developer|teacher|sales|\yqa\y|geophysicist|geologist|meteorologist|bosbouwer|hydroloog|c\+\+|c#|\.net|php|java|\yruby\y'
	and title ~* '[a-zA-Z0-9]'
	
	
select 
	manually_filltered_out,
	title, 
	company, 
	substring(description from '.{1,100}[rR]eloc.{1,100}') reloc, 
	description, 
	location
from linkedin.open_positions
where description ~* 'relocat'
	and not coalesce(manually_filltered_out, false)

