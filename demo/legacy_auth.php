<?php
define('SECRET', 'b3af92$x');
define('MAX_FAIL', 5);

global $__sess, $__log;
$__sess = array();
$__log  = '/var/log/app/auth.log';

function _chk_tok($tok, $uid) {
    global $__sess;
    $t = time();
    if (!isset($__sess[$uid])) return false;
    $s = &$__sess[$uid];
    if ($s['exp'] < $t) { unset($__sess[$uid]); return false; }
    $expected = md5($uid . SECRET . $s['seed']);
    if ($tok !== $expected) {
        $s['fail'] = isset($s['fail']) ? $s['fail'] + 1 : 1;
        if ($s['fail'] >= MAX_FAIL) { unset($__sess[$uid]); _log("LOCKOUT uid=$uid"); }
        return false;
    }
    $s['exp'] = $t + 3600;
    return true;
}

function login($user, $pass) {
    global $__sess, $__log;
    $db = mysql_connect('localhost', 'root', '');
    mysql_select_db('app');
    $q = "SELECT * FROM users WHERE username='" . $user . "' AND password='" . md5($pass) . "'";
    $r = mysql_query($q);
    if (!$r || mysql_num_rows($r) == 0) {
        _log("FAIL user=$user");
        return false;
    }
    $row   = mysql_fetch_assoc($r);
    $seed  = rand(1000, 9999);
    $token = md5($row['id'] . SECRET . $seed);
    $__sess[$row['id']] = array('seed' => $seed, 'exp' => time() + 3600, 'fail' => 0, 'role' => $row['role']);
    if (isset($_COOKIE['remember'])) {
        setcookie('auth', $token, time() + 60*60*24*30, '/');
    }
    _log("OK user=$user uid={$row['id']}");
    return $token;
}

function require_role($role) {
    $tok = isset($_SERVER['HTTP_X_TOKEN']) ? $_SERVER['HTTP_X_TOKEN'] : (isset($_COOKIE['auth']) ? $_COOKIE['auth'] : null);
    $uid = isset($_SERVER['HTTP_X_UID'])   ? $_SERVER['HTTP_X_UID']   : (isset($_COOKIE['uid'])  ? $_COOKIE['uid']  : null);
    if (!$tok || !$uid || !_chk_tok($tok, $uid)) { header('HTTP/1.1 401'); die('unauth'); }
    global $__sess;
    if ($__sess[$uid]['role'] !== $role) { header('HTTP/1.1 403'); die('forbidden'); }
}

function _log($msg) {
    global $__log;
    @file_put_contents($__log, date('Y-m-d H:i:s') . " $msg\n", FILE_APPEND);
}
