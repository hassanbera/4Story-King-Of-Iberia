#pragma once
#include "RememberLoginStore.h"

class CRememberLoginButton : public TButton
{
    CString m_endpoint;
public:
    CRememberLoginButton(TComponent *parent, LP_FRAMEDESC descriptor, const CString &endpoint)
        : TButton(parent, descriptor), m_endpoint(endpoint)
    {
        SetStateButton();
        ZeroMemory(m_menu, sizeof(m_menu));
    }

    virtual void OnLButtonDown(UINT flags, CPoint point)
    {
        BOOL wasSelected = IsStateDown();
        TButton::OnLButtonDown(flags, point);
        if(wasSelected && !IsStateDown() && !RememberLoginStore::Clear(LPCTSTR(m_endpoint)))
        {
            Select(TRUE);
            ::MessageBoxA(NULL, "Kayitli giris bilgileri silinemedi.", "King Of Iberia", MB_OK | MB_ICONERROR);
        }
    }
    virtual void OnRButtonDown(UINT, CPoint) {}
    virtual void OnRButtonUp(UINT, CPoint) {}
};
