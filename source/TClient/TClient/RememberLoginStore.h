#pragma once
#include <windows.h>
#include <wincrypt.h>
#include <string>
#include <vector>
#include <cstring>
#pragma comment(lib, "crypt32.lib")
#pragma comment(lib, "advapi32.lib")

namespace RememberLoginStore
{
    inline const char *Key() { return "Software\\4Story King Of Iberia\\RememberLogin"; }

    inline bool Clear(const char *endpoint)
    {
        HKEY key = NULL;
        LONG result = RegOpenKeyExA(HKEY_CURRENT_USER, Key(), 0, KEY_SET_VALUE, &key);
        if(result == ERROR_FILE_NOT_FOUND) return true;
        if(result != ERROR_SUCCESS) return false;
        result = RegDeleteValueA(key, endpoint);
        RegCloseKey(key);
        return result == ERROR_SUCCESS || result == ERROR_FILE_NOT_FOUND;
    }

    inline bool Save(const char *endpoint, const std::string &user, const std::string &password)
    {
        if(user.empty() || password.empty() || user.size() > 128 || password.size() > 128 ||
            user.find('\0') != std::string::npos || password.find('\0') != std::string::npos) return false;
        std::vector<BYTE> plain(user.size() + password.size() + 2, 0);
        memcpy(&plain[0], user.data(), user.size());
        memcpy(&plain[user.size() + 1], password.data(), password.size());
        DATA_BLOB input = { DWORD(plain.size()), &plain[0] }, encrypted = {0, NULL};
        BOOL protectedOK = CryptProtectData(&input, L"King Of Iberia saved login", NULL, NULL, NULL,
            CRYPTPROTECT_UI_FORBIDDEN, &encrypted);
        SecureZeroMemory(&plain[0], plain.size());
        if(!protectedOK) return false;
        HKEY key = NULL;
        LONG result = RegCreateKeyExA(HKEY_CURRENT_USER, Key(), 0, NULL, 0, KEY_SET_VALUE, NULL, &key, NULL);
        if(result == ERROR_SUCCESS)
        {
            result = RegSetValueExA(key, endpoint, 0, REG_BINARY, encrypted.pbData, encrypted.cbData);
            RegCloseKey(key);
        }
        LocalFree(encrypted.pbData);
        return result == ERROR_SUCCESS;
    }

    inline bool Load(const char *endpoint, std::string &user, std::string &password)
    {
        user.clear(); password.clear();
        HKEY key = NULL;
        if(RegOpenKeyExA(HKEY_CURRENT_USER, Key(), 0, KEY_QUERY_VALUE, &key) != ERROR_SUCCESS) return false;
        DWORD type = 0, size = 0;
        LONG result = RegQueryValueExA(key, endpoint, NULL, &type, NULL, &size);
        if(result != ERROR_SUCCESS || type != REG_BINARY || size == 0 || size > 4096)
        { RegCloseKey(key); return false; }
        std::vector<BYTE> bytes(size);
        result = RegQueryValueExA(key, endpoint, NULL, &type, &bytes[0], &size);
        RegCloseKey(key);
        if(result != ERROR_SUCCESS || type != REG_BINARY) return false;
        DATA_BLOB input = {size, &bytes[0]}, plain = {0, NULL};
        if(!CryptUnprotectData(&input, NULL, NULL, NULL, NULL, CRYPTPROTECT_UI_FORBIDDEN, &plain)) return false;
        bool valid = false;
        if(plain.cbData >= 4 && plain.cbData <= 258 && plain.pbData[plain.cbData - 1] == 0)
        {
            const char *begin = reinterpret_cast<const char *>(plain.pbData);
            size_t userSize = strlen(begin);
            if(userSize > 0 && userSize <= 128 && userSize + 2 < plain.cbData)
            {
                size_t passwordSize = strlen(begin + userSize + 1);
                if(passwordSize > 0 && passwordSize <= 128 && userSize + passwordSize + 2 == plain.cbData)
                { user.assign(begin, userSize); password.assign(begin + userSize + 1, passwordSize); valid = true; }
            }
        }
        SecureZeroMemory(plain.pbData, plain.cbData);
        LocalFree(plain.pbData);
        return valid;
    }
}
