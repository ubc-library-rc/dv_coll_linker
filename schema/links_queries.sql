
/*Dataverse names:*/
select id, alias, name from dataverse;

select dl.dataverse_id, dataverse.alias, dataverse.name, dl.linkingdataverse_id, li.alias, li.name  from dataverselinkingdataverse as dl
inner join dataverse on 
dataverse.id=dl.dataverse_id 
inner join dataverse as li
on dl.dataverse_id = li.id
where dl.linkingdataverse_id=139 order by dl.id;

\COPY ( select dl.dataverse_id, dataverse.alias, dataverse.name, dl.linkingdataverse_id, li.alias, li.name  from dataverselinkingdataverse as dl inner join dataverse on dataverse.id=dl.dataverse_id inner join dataverse as li on dl.dataverse_id = li.id where dl.linkingdataverse_id=139 order by dl.id) TO '/home/plesack/tmp/links.tsv' DELIMITER E'\t' CSV HEADER;


\COPY ( select dl.dataverse_id as child_id, dataverse.alias as child_alias, dataverse.name as child_name, 
		dl.linkingdataverse_id as parent_id, li.alias as parent_alias, li.name as parent_name  
		from dataverselinkingdataverse as dl 
		inner join dataverse on dataverse.id=dl.dataverse_id 
		inner join dataverse as li on li.dataverse_id = li.id order by dl.id) TO '/home/plesack/tmp/links.tsv' DELIMITER E'\t' CSV HEADER;

SELECT dl.dataverse_id AS child_id, dataverse.alias AS child_alias, dataverse.name AS child_name, 
		dl.linkingdataverse_id AS parent_id, parent.alias AS parent_alias, parent.name AS parent_name  
		FROM dataverselinkingdataverse AS dl 
		INNER JOIN dataverse ON dataverse.id=dl.dataverse_id 
		INNER JOIN dataverse AS parent ON parent.id = dl.linkingdataverse_id ORDER BY dl.id;


/*For migration script*/
SELECT  dl.linkingdataverse_id AS parent_id, parent.alias AS parent_alias, parent.name AS parent_name,
dl.dataverse_id AS child_id, dataverse.alias AS child_alias, dataverse.name AS child_name
FROM dataverselinkingdataverse AS dl
INNER JOIN dataverse ON dataverse.id=dl.dataverse_id
INNER JOIN dataverse AS parent ON parent.id = dl.linkingdataverse_id ORDER BY parent_id;
