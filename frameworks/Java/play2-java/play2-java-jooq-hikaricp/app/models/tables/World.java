/*
 * This file is generated by jOOQ.
 */
package models.tables;


import java.util.Collection;

import models.HelloWorld;
import models.Keys;
import models.tables.records.WorldRecord;

import org.jooq.Condition;
import org.jooq.Field;
import org.jooq.Identity;
import org.jooq.Name;
import org.jooq.PlainSQL;
import org.jooq.QueryPart;
import org.jooq.SQL;
import org.jooq.Schema;
import org.jooq.Select;
import org.jooq.Stringly;
import org.jooq.Table;
import org.jooq.TableField;
import org.jooq.TableOptions;
import org.jooq.UniqueKey;
import org.jooq.impl.DSL;
import org.jooq.impl.SQLDataType;
import org.jooq.impl.TableImpl;
import org.jooq.types.UInteger;


/**
 * This class is generated by jOOQ.
 */
@SuppressWarnings({ "all", "unchecked", "rawtypes" })
public class World extends TableImpl<WorldRecord> {

    private static final long serialVersionUID = 1L;

    /**
     * The reference instance of <code>hello_world.world</code>
     */
    public static final World WORLD = new World();

    /**
     * The class holding records for this type
     */
    @Override
    public Class<WorldRecord> getRecordType() {
        return WorldRecord.class;
    }

    /**
     * The column <code>hello_world.world.id</code>.
     */
    public final TableField<WorldRecord, UInteger> ID = createField(DSL.name("id"), SQLDataType.INTEGERUNSIGNED.nullable(false).identity(true), this, "");

    /**
     * The column <code>hello_world.world.randomNumber</code>.
     */
    public final TableField<WorldRecord, Integer> RANDOMNUMBER = createField(DSL.name("randomNumber"), SQLDataType.INTEGER.nullable(false).defaultValue(DSL.inline("0", SQLDataType.INTEGER)), this, "");

    private World(Name alias, Table<WorldRecord> aliased) {
        this(alias, aliased, (Field<?>[]) null, null);
    }

    private World(Name alias, Table<WorldRecord> aliased, Field<?>[] parameters, Condition where) {
        super(alias, null, aliased, parameters, DSL.comment(""), TableOptions.table(), where);
    }

    /**
     * Create an aliased <code>hello_world.world</code> table reference
     */
    public World(String alias) {
        this(DSL.name(alias), WORLD);
    }

    /**
     * Create an aliased <code>hello_world.world</code> table reference
     */
    public World(Name alias) {
        this(alias, WORLD);
    }

    /**
     * Create a <code>hello_world.world</code> table reference
     */
    public World() {
        this(DSL.name("world"), null);
    }

    @Override
    public Schema getSchema() {
        return aliased() ? null : HelloWorld.HELLO_WORLD;
    }

    @Override
    public Identity<WorldRecord, UInteger> getIdentity() {
        return (Identity<WorldRecord, UInteger>) super.getIdentity();
    }

    @Override
    public UniqueKey<WorldRecord> getPrimaryKey() {
        return Keys.KEY_WORLD_PRIMARY;
    }

    @Override
    public World as(String alias) {
        return new World(DSL.name(alias), this);
    }

    @Override
    public World as(Name alias) {
        return new World(alias, this);
    }

    @Override
    public World as(Table<?> alias) {
        return new World(alias.getQualifiedName(), this);
    }

    /**
     * Rename this table
     */
    @Override
    public World rename(String name) {
        return new World(DSL.name(name), null);
    }

    /**
     * Rename this table
     */
    @Override
    public World rename(Name name) {
        return new World(name, null);
    }

    /**
     * Rename this table
     */
    @Override
    public World rename(Table<?> name) {
        return new World(name.getQualifiedName(), null);
    }

    /**
     * Create an inline derived table from this table
     */
    @Override
    public World where(Condition condition) {
        return new World(getQualifiedName(), aliased() ? this : null, null, condition);
    }

    /**
     * Create an inline derived table from this table
     */
    @Override
    public World where(Collection<? extends Condition> conditions) {
        return where(DSL.and(conditions));
    }

    /**
     * Create an inline derived table from this table
     */
    @Override
    public World where(Condition... conditions) {
        return where(DSL.and(conditions));
    }

    /**
     * Create an inline derived table from this table
     */
    @Override
    public World where(Field<Boolean> condition) {
        return where(DSL.condition(condition));
    }

    /**
     * Create an inline derived table from this table
     */
    @Override
    @PlainSQL
    public World where(SQL condition) {
        return where(DSL.condition(condition));
    }

    /**
     * Create an inline derived table from this table
     */
    @Override
    @PlainSQL
    public World where(@Stringly.SQL String condition) {
        return where(DSL.condition(condition));
    }

    /**
     * Create an inline derived table from this table
     */
    @Override
    @PlainSQL
    public World where(@Stringly.SQL String condition, Object... binds) {
        return where(DSL.condition(condition, binds));
    }

    /**
     * Create an inline derived table from this table
     */
    @Override
    @PlainSQL
    public World where(@Stringly.SQL String condition, QueryPart... parts) {
        return where(DSL.condition(condition, parts));
    }

    /**
     * Create an inline derived table from this table
     */
    @Override
    public World whereExists(Select<?> select) {
        return where(DSL.exists(select));
    }

    /**
     * Create an inline derived table from this table
     */
    @Override
    public World whereNotExists(Select<?> select) {
        return where(DSL.notExists(select));
    }
}
