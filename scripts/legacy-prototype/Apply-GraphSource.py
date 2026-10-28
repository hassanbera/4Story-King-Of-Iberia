from pathlib import Path

path = Path(__file__).resolve().parent / "Source 3.3" / "TServer" / "TMapSvr" / "TMonster.cpp"
data = path.read_bytes()
include = b'#include "TMapSvrModule.h"\r\n'
if data.count(include) != 1 or b'#include "AmbientRoutes.h"' in data:
    raise RuntimeError("Unexpected source include state")
data = data.replace(include, include + b'#include "AmbientRoutes.h"\r\n')

branch = r'''
    // Ambient route graphs are selected per resident spawn. A chosen
    // distant stop is reached along graph edges, never by a direct shortcut.
    WORD wGraphID = m_pSPAWN->m_pSPAWN->m_bRoamType == 5 ?
        AmbientRoutes::GraphForSpawn(m_pSPAWN->m_pSPAWN->m_wMapID,
            m_pSPAWN->m_pSPAWN->m_wID) : 0;
    if(m_pSPAWN->m_pSPAWN->m_bRoamType == 5 && m_bMode == MT_NORMAL &&
        AmbientRoutes::NodeCount(wGraphID) >= 3)
    {
        BYTE bCount = AmbientRoutes::NodeCount(wGraphID);
        BYTE bNode = m_bCurPathID;
        if(m_bCurPathDir <= 1 || bNode >= bCount)
        {
            bNode = AmbientRoutes::NearestNode(wGraphID, m_fPosX, m_fPosY, m_fPosZ);
            if(bNode != 255)
            {
                m_bCurPathID = bNode;
                m_bCurPathDir = 1;
            }
        }
        if(bNode != 255)
        {
            if(fabs(m_fPosY - pHOST->m_fPosY) > MAX_ROAMHEIGHT ||
                GetDistance(m_fPosX, m_fPosZ, pHOST->m_fPosX, pHOST->m_fPosZ) > MAX_ROAMBOUND)
                return FALSE;

            const AmbientRoutes::Node *pNode = AmbientRoutes::GetNode(wGraphID, bNode);
            if(!pNode)
                return FALSE;
            if(GetDistance(pNode->x, pNode->z, m_fPosX, m_fPosZ) <= ZONE_HOMESIZE)
            {
                if(DWORD(rand() % 100) < pNode->stopProbability)
                {
                    bAction = TA_STAND;
                    return TRUE;
                }
                BYTE bGoal = m_bCurPathDir > 1 ? BYTE(m_bCurPathDir - 2) : bNode;
                if(bGoal >= bCount || bGoal == bNode)
                {
                    bGoal = AmbientRoutes::ChooseDistantGoal(wGraphID, bNode);
                    if(bGoal == 255)
                        return FALSE;
                    m_bCurPathDir = BYTE(bGoal + 2);
                }
                BYTE bNext = AmbientRoutes::NextHop(wGraphID, bNode, bGoal);
                if(bNext == 255 || bNext == bNode)
                    return FALSE;
                m_bCurPathID = bNext;
                pNode = AmbientRoutes::GetNode(wGraphID, bNext);
                m_fStartX = m_fPosX;
                m_fStartY = m_fPosY;
                m_fStartZ = m_fPosZ;
            }

            FLOAT fRad = FLOAT(rand() % 360) * FLOAT(M_PI) / 180.0f;
            fPosX = pNode->x + pNode->radius * cosf(fRad);
            fPosY = pNode->y;
            fPosZ = pNode->z + pNode->radius * sinf(fRad);
            bAction = rand() % 100 < 25 ? TA_RUN : TA_WALK;
            return TRUE;
        }
    }

'''.replace("\n", "\r\n").replace("    ", "\t").encode("ascii")
anchor = b'\t// Type 5 is reserved for ambient residents.'
if data.count(anchor) != 1 or b'Ambient route graphs are shared' in data:
    raise RuntimeError("Unexpected ambient branch state")
data = data.replace(anchor, branch + anchor)
path.write_bytes(data)
print("Graph movement branch applied")
