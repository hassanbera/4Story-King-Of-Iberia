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
        if(!CanProcess() || !HitTest(point)) return;
        ToggleRemember();
    }
    void ToggleRemember()
    {
        BOOL wasSelected = IsStateDown();
        Select(!wasSelected);
        if(wasSelected && !IsStateDown() && !RememberLoginStore::Clear(LPCTSTR(m_endpoint)))
        {
            Select(TRUE);
            ::MessageBoxA(NULL, "Kayitli giris bilgileri silinemedi.", "King Of Iberia", MB_OK | MB_ICONERROR);
        }
    }
    virtual void OnRButtonDown(UINT, CPoint) {}
    virtual void OnRButtonUp(UINT, CPoint) {}
};

class CRememberLoginLabel : public TComponent
{
    CRememberLoginButton *m_checkbox;
public:
    CRememberLoginLabel(TComponent *parent, CRememberLoginButton *checkbox)
        : TComponent(parent, NULL), m_checkbox(checkbox) {}
    virtual void OnLButtonDown(UINT, CPoint point)
    {
        if(CanProcess() && HitTest(point)) m_checkbox->ToggleRemember();
    }
};
