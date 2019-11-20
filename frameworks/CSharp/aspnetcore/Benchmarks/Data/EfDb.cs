﻿// Copyright (c) .NET Foundation. All rights reserved.
// Licensed under the Apache License, Version 2.0. See License.txt in the project root for license information.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Benchmarks.Configuration;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Query;
using Microsoft.Extensions.Options;

namespace Benchmarks.Data
{
    public class EfDb : IDb
    {
        private readonly IRandom _random;
        private readonly ApplicationDbContext _dbContext;

        public EfDb(IRandom random, ApplicationDbContext dbContext, IOptions<AppSettings> appSettings)
        {
            _random = random;
            _dbContext = dbContext;
        }

        private static readonly Func<ApplicationDbContext, int, Task<World>> _firstWorldQuery
            = EF.CompileAsyncQuery((ApplicationDbContext context, int id)
                => context.World.First(w => w.Id == id));

        public Task<World> LoadSingleQueryRow()
        {
            var id = _random.Next(1, 10001);

            // TODO: compiled queries are not supported in EF 3.0-preview7
            // return _firstWorldQuery(_dbContext, id);
            
            return _dbContext.World.FirstAsync(w => w.Id == id);
        }

        public async Task<World[]> LoadMultipleQueriesRows(int count)
        {
            var result = new World[count];

            for (var i = 0; i < count; i++)
            {
                var id = _random.Next(1, 10001);

                // TODO: compiled queries are not supported in EF 3.0-preview7
                // result[i] = await _firstWorldQuery(_dbContext, id);

                result[i] = await _dbContext.World.FirstAsync(w => w.Id == id);
            }

            return result;
        }

        private static readonly Func<ApplicationDbContext, int, Task<World>> _firstWorldTrackedQuery
            = EF.CompileAsyncQuery((ApplicationDbContext context, int id)
                => context.World.AsTracking().First(w => w.Id == id));

        public async Task<World[]> LoadMultipleUpdatesRows(int count)
        {
            var results = new World[count];
            
            for (var i = 0; i < count; i++)
            {
                var id = _random.Next(1, 10001);
            
                // TODO: compiled queries are not supported in EF 3.0-preview7
                // var result = await _firstWorldTrackedQuery(_dbContext, id);

                var result = await _dbContext.World.AsTracking().FirstAsync(w => w.Id == id);

                var oldId = (int) _dbContext.Entry(result).Property("RandomNumber").CurrentValue;
               
                // EF automatically detects changes, and would not create an UPDATE statement if the new value
                // is equal to the current one. We need to keep generating random numbers until there is no collision.
                
                while (true)
                {
                   var newId = _random.Next(1, 10001);
                   
                   if (newId != oldId)
                   {
                        _dbContext.Entry(result).Property("RandomNumber").CurrentValue = newId;
                        break;
                   }
                };
                
                results[i] = result;
            }

            await _dbContext.SaveChangesAsync();

            return results;
        }

        private static readonly Func<ApplicationDbContext, IAsyncEnumerable<Fortune>> _fortunesQuery
            = EF.CompileAsyncQuery((ApplicationDbContext context) => context.Fortune);

        public async Task<List<Fortune>> LoadFortunesRows()
        {
            var result = await _dbContext.Fortune.ToListAsync();

            // TODO: compiled queries are not supported in EF 3.0-preview7
            // await foreach (var element in _fortunesQuery(_dbContext))

            result.Add(new Fortune { Message = "Additional fortune added at request time." });
            result.Sort();

            return result;
        }
    }
}
