﻿module Stock

open Giraffe
open Dapper
open Npgsql
open Models
open FSharp.Control.Tasks
open Giraffe.ViewEngine

let application : HttpHandler = 
    
    let fortunes : HttpHandler = 
        let extra = {id = 0; message = "Additional fortune added at request time."}

        fun _ ctx ->
            task {
                use conn = new NpgsqlConnection(ConnectionString)
                let! data = conn.QueryAsync<Fortune>("SELECT id, message FROM fortune")

                let view =
                    let xs = data.AsList()
                    xs.Add extra
                    xs.Sort FortuneComparer
                    HtmlViews.fortunes xs

                let bytes = 
                    view 
                    |> RenderView.AsBytes.xmlNode

                ctx.SetContentType "text/html;charset=utf-8"
                return! ctx.WriteBytesAsync bytes
            }

    choose [
        route "/plaintext" >=> text "Hello, World!" 
        route "/json" >=> json {| message = "Hello, World!" |}
        route "/fortunes" >=> fortunes
    ]
