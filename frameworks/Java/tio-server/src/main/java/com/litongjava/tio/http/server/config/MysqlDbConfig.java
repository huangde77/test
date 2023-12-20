package com.litongjava.tio.http.server.config;

import com.jfinal.plugin.activerecord.ActiveRecordPlugin;
import com.jfinal.plugin.activerecord.OrderedFieldContainerFactory;
import com.jfinal.plugin.hikaricp.HikariCpPlugin;
import com.litongjava.tio.utils.enviorment.EnviormentUtils;

public class MysqlDbConfig {

  public void init() {
    // start active recored
    String jdbcUrl = EnviormentUtils.get("jdbc.url");
    // String jdbcUrl = "jdbc:mysql://192.168.3.9/hello_world";

    String jdbcUser = EnviormentUtils.get("jdbc.user");
//    String jdbcUser = "root";

    String jdbcPswd = EnviormentUtils.get("jdbc.pswd");
//    String jdbcPswd = "robot_123456#";
    HikariCpPlugin hikariCpPlugin = new HikariCpPlugin(jdbcUrl, jdbcUser, jdbcPswd);

    ActiveRecordPlugin arp = new ActiveRecordPlugin(hikariCpPlugin);
    arp.setContainerFactory(new OrderedFieldContainerFactory());

//    Engine engine = arp.getEngine();
//    engine.setSourceFactory(new ClassPathSourceFactory());
//    engine.setCompressorOn(' ');
//    engine.setCompressorOn('\n');
    // arp.addSqlTemplate("/sql/all_sqls.sql");
//    arp.start();
    hikariCpPlugin.start();
    arp.start();
  }
}
