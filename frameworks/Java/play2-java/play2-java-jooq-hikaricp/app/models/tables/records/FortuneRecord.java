/*
 * This file is generated by jOOQ.
 */
package models.tables.records;


import models.tables.Fortune;

import org.jooq.Record1;
import org.jooq.impl.UpdatableRecordImpl;
import org.jooq.types.UInteger;


/**
 * This class is generated by jOOQ.
 */
@SuppressWarnings({ "all", "unchecked", "rawtypes" })
public class FortuneRecord extends UpdatableRecordImpl<FortuneRecord> {

    private static final long serialVersionUID = 1L;

    /**
     * Setter for <code>hello_world.fortune.id</code>.
     */
    public void setId(UInteger value) {
        set(0, value);
    }

    /**
     * Getter for <code>hello_world.fortune.id</code>.
     */
    public UInteger getId() {
        return (UInteger) get(0);
    }

    /**
     * Setter for <code>hello_world.fortune.message</code>.
     */
    public void setMessage(String value) {
        set(1, value);
    }

    /**
     * Getter for <code>hello_world.fortune.message</code>.
     */
    public String getMessage() {
        return (String) get(1);
    }

    // -------------------------------------------------------------------------
    // Primary key information
    // -------------------------------------------------------------------------

    @Override
    public Record1<UInteger> key() {
        return (Record1) super.key();
    }

    // -------------------------------------------------------------------------
    // Constructors
    // -------------------------------------------------------------------------

    /**
     * Create a detached FortuneRecord
     */
    public FortuneRecord() {
        super(Fortune.FORTUNE);
    }

    /**
     * Create a detached, initialised FortuneRecord
     */
    public FortuneRecord(UInteger id, String message) {
        super(Fortune.FORTUNE);

        setId(id);
        setMessage(message);
        resetChangedOnNotNull();
    }
}
