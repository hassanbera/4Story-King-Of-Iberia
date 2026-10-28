#include "RememberLoginStore.h"
#include <cassert>
#include <iostream>

int main()
{
    const char *endpoint = "test-only:remember-login";
    const char *other = "test-only:other-server";
    std::string user, password;
    assert(RememberLoginStore::Clear(endpoint));
    assert(!RememberLoginStore::Load(endpoint, user, password));
    assert(RememberLoginStore::Save(endpoint, "DummyUser", "DummyPassword-42"));
    assert(RememberLoginStore::Load(endpoint, user, password));
    assert(user == "DummyUser" && password == "DummyPassword-42");
    assert(!RememberLoginStore::Load(other, user, password));
    assert(user.empty() && password.empty());
    assert(!RememberLoginStore::Save(endpoint, "", "invalid"));
    HKEY key = NULL;
    assert(RegOpenKeyExA(HKEY_CURRENT_USER, RememberLoginStore::Key(), 0, KEY_QUERY_VALUE | KEY_SET_VALUE, &key) == ERROR_SUCCESS);
    BYTE bytes[4096]; DWORD type = 0, size = sizeof(bytes);
    assert(RegQueryValueExA(key, endpoint, NULL, &type, bytes, &size) == ERROR_SUCCESS && type == REG_BINARY);
    std::string cipher(reinterpret_cast<char *>(bytes), size);
    assert(cipher.find("DummyUser") == std::string::npos && cipher.find("DummyPassword-42") == std::string::npos);
    const BYTE corrupt[] = {1, 2, 3};
    assert(RegSetValueExA(key, endpoint, 0, REG_BINARY, corrupt, sizeof(corrupt)) == ERROR_SUCCESS);
    RegCloseKey(key);
    assert(!RememberLoginStore::Load(endpoint, user, password));
    assert(RememberLoginStore::Clear(endpoint));
    assert(!RememberLoginStore::Load(endpoint, user, password));
    std::cout << "DPAPI roundtrip, server scope, encrypted storage, corrupt data and removal passed.\n";
    return 0;
}
