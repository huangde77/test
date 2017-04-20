package com.techempower.act.sql.controller;

import com.techempower.act.controller.WorldControllerBase;
import com.techempower.act.domain.IWorld;
import com.techempower.act.sql.domain.World;

import java.util.ArrayList;
import java.util.List;

public abstract class SqlWorldControllerBase<
        MODEL_TYPE extends IWorld,
        DAO_TYPE extends World.WorldDao<MODEL_TYPE>>
        extends WorldControllerBase<MODEL_TYPE, DAO_TYPE> {

    private boolean batchUpdate;

    public SqlWorldControllerBase(boolean batch) {
        this.batchUpdate = batch;
    }

    protected List<MODEL_TYPE> doUpdate(int q) {
        if (batchUpdate) {
            return doBatchUpdate(q);
        }
        List<MODEL_TYPE> retVal = new ArrayList<>();
        for (int i = 0; i < q; ++i) {
            MODEL_TYPE world = findAndModifyOne();
            worldDao().update(world.getRandomNumber(), world.getId());
            retVal.add(world);
        }
        return retVal;
    }

    private List<MODEL_TYPE> doBatchUpdate(int q) {
        List<MODEL_TYPE> retVal = new ArrayList<>();
        for (int i = 0; i < q; ++i) {
            MODEL_TYPE world = findAndModifyOne();
            retVal.add(world);
        }
        worldDao().insertBatch(retVal);
        return retVal;
    }

}
