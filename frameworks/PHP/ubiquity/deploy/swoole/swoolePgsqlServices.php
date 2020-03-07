<?php
\Ubiquity\cache\CacheManager::startProd($config);
\Ubiquity\orm\DAO::setModelsDatabases([
	'models\\Fortune' => 'pgsql',
	'models\\World' => 'pgsql'
]);
\Ubiquity\cache\CacheManager::warmUpControllers([
	'controllers\\PlaintextAsync',
	'controllers\\JsonAsync',
	'controllers\\DbPg',
	'controllers\\FortunesPg'
]);
$swooleServer->on('workerStart', function ($srv) use (&$config) {
	\Ubiquity\orm\DAO::startDatabase($config, 'pgsql');
	\Ubiquity\orm\DAO::prepareGetById('world', 'models\\World');
	\Ubiquity\orm\DAO::prepareGetAll('fortune', 'models\\Fortune');
});
