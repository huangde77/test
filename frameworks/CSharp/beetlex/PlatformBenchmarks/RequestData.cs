﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PlatformBenchmarks
{
    public class RequestData : IDisposable
    {
        public ArraySegment<byte> Data { get; set; }

        public ReadOnlySpan<byte> GetSpan()
        {
            return new ReadOnlySpan<byte>(Data.Array, Data.Offset, Data.Count);
        }

        public void Dispose()
        {
            System.Buffers.ArrayPool<byte>.Shared.Return(Data.Array);
        }
    }
}
