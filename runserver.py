# encoding: utf8

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import redis
import time
from datetime import datetime, timedelta

app = Flask(__name__)


app.secret_key = "lasfuoi3ro8w7gfow3bwiubdwoeg7p23r8g23rg"

serverinfo_meta = {
    "aof_current_rewrite_time_sec": "Duration of the on-going AOF rewrite operation if any",
    "aof_enabled": "Flag indicating AOF logging is activated",
    "aof_last_bgrewrite_status": "Status of the last AOF rewrite operation",
    "aof_last_rewrite_time_sec": "Duration of the last AOF rewrite operation in seconds",
    "aof_last_write_status": "Status of last AOF write operation",
    "aof_rewrite_in_progress": "Flag indicating a AOF rewrite operation is on-going",
    "aof_rewrite_scheduled": "Flag indicating an AOF rewrite operation will be scheduled once the on-going RDB save is complete",
    "arch_bits": "Architecture (32 or 64 bits)",
    "blocked_clients": "Number of clients pending on a blocking call (BLPOP, BRPOP, BRPOPLPUSH)",
    "client_biggest_input_buf": "biggest input buffer among current client connections",
    "client_longest_output_list": None,
    "cmdstat_client": "Statistics for the client command",
    "cmdstat_config": "Statistics for the config command",
    "cmdstat_dbsize": "Statistics for the dbsize command",
    "cmdstat_del": "Statistics for the del command",
    "cmdstat_dump": "Statistics for the dump command",
    "cmdstat_expire": "Statistics for the expire command",
    "cmdstat_flushall": "Statistics for the flushall command",
    "cmdstat_get":"Statistics for the get command",
    "cmdstat_hgetall": "Statistics for the hgetall command",
    "cmdstat_hkeys": "Statistics for the hkeys command",
    "cmdstat_hmset": "Statistics for the hmset command",
    "cmdstat_info": "Statistics for the info command",
    "cmdstat_keys": "Statistics for the keys command",
    "cmdstat_llen": "Statistics for the llen command",
    "cmdstat_ping": "Statistics for the ping command",
    "cmdstat_psubscribe": "Statistics for the psubscribe command",
    "cmdstat_pttl": "Statistics for the pttl command",
    "cmdstat_sadd": "Statistics for the sadd command",
    "cmdstat_scan": "Statistics for the scan command",
    "cmdstat_select": "Statistics for the select command",
    "cmdstat_set": "Statistics for the set command",
    "cmdstat_smembers": "Statistics for the smembers command",
    "cmdstat_sscan": "Statistics for the sscan command",
    "cmdstat_ttl": "Statistics for the ttl command",
    "cmdstat_type": "Statistics for the type command",
    "cmdstat_zadd": "Statistics for the zadd command",
    "cmdstat_zcard": "Statistics for the zcard command",
    "cmdstat_zrange": "Statistics for the zrange command",
    "cmdstat_zremrangebyrank": "Statistics for the zremrangebyrank command",
    "cmdstat_zrevrange": "Statistics for the zrevrange command",
    "cmdstat_zscan": "Statistics for the zscan command",
    "config_file": None,
    "connected_clients": None,
    "connected_slaves": None,
    "db0": None,
    "evicted_keys": None,
    "expired_keys": None,
    "gcc_version": None,
    "hz": None,
    "instantaneous_ops_per_sec": None,
    "keyspace_hits": None,
    "keyspace_misses": None,
    "latest_fork_usec": None,
    "loading": None,
    "lru_clock": None,
    "master_repl_offset": None,
    "mem_allocator": None,
    "mem_fragmentation_ratio": None,
    "multiplexing_api": None,
    "os": None,
    "process_id": None,
    "pubsub_channels": None,
    "pubsub_patterns": None,
    "rdb_bgsave_in_progress": None,
    "rdb_changes_since_last_save": None,
    "rdb_current_bgsave_time_sec": None,
    "rdb_last_bgsave_status": None,
    "rdb_last_bgsave_time_sec": None,
    "rdb_last_save_time": None,
    "redis_build_id": None,
    "redis_git_dirty": None,
    "redis_git_sha1": None,
    "redis_mode": None,
    "redis_version": None,
    "rejected_connections": None,
    "repl_backlog_active": None,
    "repl_backlog_first_byte_offset": None,
    "repl_backlog_histlen": None,
    "repl_backlog_size": None,
    "role": None,
    "run_id": None,
    "sync_full": None,
    "sync_partial_err": None,
    "sync_partial_ok": None,
    "tcp_port": None,
    "total_commands_processed": None,
    "total_connections_received": None,
    "uptime_in_days": None,
    "uptime_in_seconds": None,
    "used_cpu_sys": None,
    "used_cpu_sys_children": None,
    "used_cpu_user": None,
    "used_cpu_user_children": None,
    "used_memory": None,
    "used_memory_human": None,
    "used_memory_lua": None,
    "used_memory_peak": None,
    "used_memory_peak_human": None,
    "used_memory_rss": None
}


@app.route("/", methods=['GET', 'POST'])
def login():
    """
    Start page
    """
    if request.method == 'POST':
        # TODO: test connection, handle failures
        host = request.args.get("host", "localhost")
        port = int(request.args.get("port", "6379"))
        db = int(request.args.get("db", "0"))
        url = url_for('server_db', host=host, port=port, db=db)
        return redirect(url)
    else: 
        s = time.time()
        return render_template('login.html',
            duration=time.time()-s)


@app.route("/<host>:<int:port>/<int:db>/")
def server_db(host, port, db):
    """
    List all databases and show info on server
    """
    s = time.time()
    r = redis.StrictRedis(host=host, port=port, db=0)
    info = r.info("all")
    return render_template('server.html',
        host=host,
        port=port,
        db=db,
        info=info,
        serverinfo_meta=serverinfo_meta,
        duration=time.time()-s)


@app.route("/<host>:<int:port>/<int:db>/keys/", methods=['GET', 'POST'])
def keys(host, port, db):
    """
    List keys for one database
    """
    s = time.time()
    r = redis.StrictRedis(host=host, port=port, db=db)
    if request.method == "POST":
        action = request.form["action"]
        app.logger.debug(action)
        if action == "delkey":
            if request.form["key"] is not None:
                result = r.delete(request.form["key"])
                if result == 1:
                    flash("Key %s has been deleted." % request.form["key"], category="info")
                else:
                    flash("Key %s could not be deleted." % request.form["key"], category="error")
        return redirect(request.url)
    else:
        offset = int(request.args.get("offset", "0"))
        perpage = int(request.args.get("perpage", "10"))
        pattern = request.args.get('pattern', '*')
        dbsize = r.dbsize()
        keys = sorted(r.keys(pattern))
        limited_keys = keys[offset:(perpage+offset)]
        types = {}
        for key in limited_keys:
            types[key] = r.type(key)
        return render_template('keys.html',
            host=host,
            port=port,
            db=db,
            dbsize=dbsize,
            keys=limited_keys,
            types=types,
            offset=offset,
            perpage=perpage,
            pattern=pattern,
            num_keys=len(keys),
            duration=time.time()-s)


@app.route("/<host>:<int:port>/<int:db>/keys/<key>/")
def key(host, port, db, key):
    """
    Show a specific key
    """
    s = time.time()
    r = redis.StrictRedis(host=host, port=port, db=db)
    dump = r.dump(key)
    if dump is None:
        abort(404)
    #if t is None:
    #    abort(404)
    size = len(dump)
    del dump
    t = r.type(key)
    ttl = r.pttl(key)
    if t == "string":
        val = r.get(key)
    elif t == "list":
        val = r.lrange(key, 0, -1)
    elif t == "hash":
        val = r.hgetall(key)
    elif t == "set":
        val = r.smembers(key)
    elif t == "zset":
        val = r.zrange(key, 0, -1)
    return render_template('key.html',
        host=host,
        port=port,
        db=db,
        key=key,
        value=val,
        type=t,
        size=size,
        ttl=ttl / 1000.0,
        now=datetime.utcnow(),
        expiration=datetime.utcnow() + timedelta(seconds=ttl / 1000.0),
        duration=time.time()-s)


if __name__ == "__main__":
    app.run(debug=True, port=5001)