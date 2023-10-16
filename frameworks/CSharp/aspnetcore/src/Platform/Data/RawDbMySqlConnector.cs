﻿// Copyright (c) .NET Foundation. All rights reserved.
// Licensed under the Apache License, Version 2.0. See License.txt in the project root for license information.

#if MYSQLCONNECTOR

using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Threading.Tasks;
using Microsoft.Extensions.Caching.Memory;
using MySqlConnector;

namespace PlatformBenchmarks;

// Is semantically identical to RawDbNpgsql.cs.
// If you are changing RawDbMySqlConnector.cs, also consider changing RawDbNpgsql.cs.
public sealed class RawDb
{
    private readonly ConcurrentRandom _random;
    private readonly string _connectionString;
    private readonly MemoryCache _cache
        = new(new MemoryCacheOptions { ExpirationScanFrequency = TimeSpan.FromMinutes(60) });

    private readonly MySqlDataSource _dataSource;

    public RawDb(ConcurrentRandom random, AppSettings appSettings)
    {
        _random = random;
        _connectionString = appSettings.ConnectionString;
        _dataSource = new MySqlDataSource(appSettings.ConnectionString);
    }

    public async Task<World> LoadSingleQueryRow()
    {
        using var db = CreateConnection();
        await db.OpenAsync();

        var (cmd, _) = await CreateReadCommandAsync(db);
        using var command = cmd;

        return await ReadSingleRow(cmd);
    }

    public Task<CachedWorld[]> LoadCachedQueries(int count)
    {
        var result = new CachedWorld[count];
        var cacheKeys = _cacheKeys;
        var cache = _cache;
        var random = _random;
        for (var i = 0; i < result.Length; i++)
        {
            var id = random.Next(1, 10001);
            var key = cacheKeys[id];
            if (cache.TryGetValue(key, out var cached))
            {
                result[i] = (CachedWorld)cached;
            }
            else
            {
                return LoadUncachedQueries(id, i, count, this, result);
            }
        }

        return Task.FromResult(result);

        static async Task<CachedWorld[]> LoadUncachedQueries(int id, int i, int count, RawDb rawdb, CachedWorld[] result)
        {
            using var db = rawdb.CreateConnection();
            await db.OpenAsync();

            var (cmd, idParameter) = await rawdb.CreateReadCommandAsync(db);
            using var command = cmd;
            async Task<CachedWorld> create(ICacheEntry _) => await rawdb.ReadSingleRow(cmd);

            var cacheKeys = _cacheKeys;
            var key = cacheKeys[id];

            idParameter.Value = id;

            for (; i < result.Length; i++)
            {
                result[i] = await rawdb._cache.GetOrCreateAsync(key, create);

                id = rawdb._random.Next(1, 10001);
                idParameter.Value = id;
                key = cacheKeys[id];
            }

            return result;
        }
    }

    public async Task PopulateCache()
    {
        using (var db = new MySqlConnection(_connectionString))
        {
            await db.OpenAsync();

            var (cmd, idParameter) = await CreateReadCommandAsync(db);
            using (cmd)
            {
                var cacheKeys = _cacheKeys;
                var cache = _cache;
                for (var i = 1; i < 10001; i++)
                {
                    idParameter.Value = i;
                    cache.Set<CachedWorld>(cacheKeys[i], await ReadSingleRow(cmd));
                }
            }
        }

        Console.WriteLine("Caching Populated");
    }

    public async Task<World[]> LoadMultipleQueriesRows(int count)
    {
        var results = new World[count];

        using var connection = await _dataSource.OpenConnectionAsync();

        using var batch = new MySqlBatch(connection);

        for (var i = 0; i < count; i++)
        {
            batch.BatchCommands.Add(new MySqlBatchCommand()
            {
                CommandText = "SELECT id, randomnumber FROM world WHERE id = @id",
                Parameters = { new MySqlParameter("@id", _random.Next(1, 10001)) }
            });
        }

        using var reader = await batch.ExecuteReaderAsync();

        for (var i = 0; i < count; i++)
        {
            await reader.ReadAsync();
            results[i] = new World { Id = reader.GetInt32(0), RandomNumber = reader.GetInt32(1) };
            await reader.NextResultAsync();
        }

        return results;
    }

    public async Task<World[]> LoadMultipleUpdatesRows(int count)
    {
        var results = new World[count];

        using var connection = CreateConnection();
        await connection.OpenAsync();

        var (queryCmd, queryParameter) = await CreateReadCommandAsync(connection);
        using (queryCmd)
        {
            for (var i = 0; i < results.Length; i++)
            {
                results[i] = await ReadSingleRow(queryCmd);
                queryParameter.Value = _random.Next(1, 10001);
            }
        }

        using (var updateCmd = new MySqlCommand(BatchUpdateString.Query(count), connection))
        {
            for (var i = 0; i < results.Length; i++)
            {
                var randomNumber = _random.Next(1, 10001);

                updateCmd.Parameters.Add(new MySqlParameter { Value = results[i].Id });
                updateCmd.Parameters.Add(new MySqlParameter { Value = randomNumber });

                results[i].RandomNumber = randomNumber;
            }

            await updateCmd.ExecuteNonQueryAsync();
        }

        return results;
    }

    public async Task<List<FortuneUtf8>> LoadFortunesRows()
    {
        // Benchmark requirements explicitly prohibit pre-initializing the list size
        var result = new List<FortuneUtf8>();

        var db = CreateConnection();
        await db.OpenAsync();

        using var cmd = new MySqlCommand("SELECT id, message FROM fortune", db);
        using var rdr = await cmd.ExecuteReaderAsync();

        while (await rdr.ReadAsync())
        {
            result.Add(new FortuneUtf8
            (
                id: rdr.GetInt32(0),
                message: rdr.GetFieldValue<byte[]>(1)
            ));
        }

        result.Add(new FortuneUtf8(id: 0, AdditionalFortune));
        result.Sort();

        return result;
    }

    private readonly byte[] AdditionalFortune = "Additional fortune added at request time."u8.ToArray();

    private async Task<(MySqlCommand readCmd, MySqlParameter idParameter)> CreateReadCommandAsync(MySqlConnection connection)
    {
        var cmd = new MySqlCommand("SELECT id, randomnumber FROM world WHERE id = @Id", connection);
        var parameter = new MySqlParameter("@Id", _random.Next(1, 10001));

        cmd.Parameters.Add(parameter);

        await cmd.PrepareAsync();
            
        return (cmd, parameter);
    }
        
    [MethodImpl(MethodImplOptions.AggressiveInlining)]
    private async Task<World> ReadSingleRow(MySqlCommand cmd)
    {
        using (var rdr = await cmd.ExecuteReaderAsync(System.Data.CommandBehavior.SingleRow))
        {
            await rdr.ReadAsync();

            return new World
            {
                Id = rdr.GetInt32(0),
                RandomNumber = rdr.GetInt32(1)
            };
        }
    }

    private MySqlConnection CreateConnection() => _dataSource.CreateConnection();

    private static readonly object[] _cacheKeys = Enumerable.Range(0, 10001).Select((i) => new CacheKey(i)).ToArray();

    public sealed class CacheKey : IEquatable<CacheKey>
    {
        private readonly int _value;

        public CacheKey(int value)
            => _value = value;

        public bool Equals(CacheKey key)
            => key._value == _value;

        public override bool Equals(object obj)
            => ReferenceEquals(obj, this);

        public override int GetHashCode()
            => _value;

        public override string ToString()
            => _value.ToString();
    }
}

#endif