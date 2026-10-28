from pathlib import Path

ROOT = Path(__file__).resolve().parent / "Source 3.3" / "TServer" / "TMapSvr"


def replace_once(name: str, old: bytes, new: bytes) -> None:
    path = ROOT / name
    data = path.read_bytes()
    if data.count(old) != 1:
        raise RuntimeError(f"Expected one match in {path.name}, found {data.count(old)}")
    path.write_bytes(data.replace(old, new))


replace_once(
    "TAICmdRoam.cpp",
    b'{\r\n\tif(!m_dwDelay)\r\n',
    b'{\r\n'
    b'\t// Ambient residents get a bounded, varied pause.\r\n'
    b'\tif(pMON->m_pSPAWN && pMON->m_pSPAWN->m_pSPAWN &&\r\n'
    b'\t\tpMON->m_pSPAWN->m_pSPAWN->m_bRoamType == 5)\r\n'
    b'\t\treturn 1000 + rand() % 4000;\r\n\r\n'
    b'\tif(!m_dwDelay)\r\n',
)

route_branch = r'''
    // Type 5 is reserved for ambient residents. Pick a distant stop and
    // travel there through adjacent, ordered path points.
    if(m_pSPAWN->m_pSPAWN->m_bRoamType == 5 && m_bMode == MT_NORMAL &&
        m_pSPAWN->m_pSPAWN->m_vPathPoint.size() >= 3 &&
        m_pSPAWN->m_pSPAWN->m_vPathPoint.size() <= 200)
    {
        VPATHPOINT &vPath = m_pSPAWN->m_pSPAWN->m_vPathPoint;
        const BYTE bCount = BYTE(vPath.size());
        if(m_bCurPathID >= bCount)
        {
            m_bCurPathID = 0;
            m_bCurPathDir = 1;
        }

        if(fabs(m_fPosY - pHOST->m_fPosY) > MAX_ROAMHEIGHT ||
            GetDistance(m_fPosX, m_fPosZ, pHOST->m_fPosX, pHOST->m_fPosZ) > MAX_ROAMBOUND)
            return FALSE;

        LPTPATHPOINT pCurrent = vPath[m_bCurPathID];
        if(GetDistance(pCurrent->m_fPosX, pCurrent->m_fPosZ,
            m_fPosX, m_fPosZ) <= ZONE_HOMESIZE)
        {
            if(DWORD(rand() % 100) < pCurrent->m_bProb)
            {
                bAction = TA_STAND;
                return TRUE;
            }

            // The old path direction byte holds goal index + 2 for type 5.
            // A value of 1 is the existing spawn/respawn sentinel.
            BYTE bGoal = m_bCurPathDir > 1 ? BYTE(m_bCurPathDir - 2) : m_bCurPathID;
            if(bGoal >= bCount || bGoal == m_bCurPathID)
            {
                DWORD dwTotalWeight = 0;
                for(BYTE i=0; i<bCount; i++)
                {
                    if(i == m_bCurPathID ||
                        (bCount >= 4 && abs(INT(i) - INT(m_bCurPathID)) < 2))
                        continue;
                    DWORD dwDistance = DWORD(GetDistance(pCurrent->m_fPosX,
                        pCurrent->m_fPosZ, vPath[i]->m_fPosX, vPath[i]->m_fPosZ));
                    dwTotalWeight += max(DWORD(1), dwDistance);
                }
                if(!dwTotalWeight)
                    return FALSE;
                DWORD dwPick = DWORD(rand()) % dwTotalWeight;
                for(BYTE j=0; j<bCount; j++)
                {
                    if(j == m_bCurPathID ||
                        (bCount >= 4 && abs(INT(j) - INT(m_bCurPathID)) < 2))
                        continue;
                    DWORD dwDistance = DWORD(GetDistance(pCurrent->m_fPosX,
                        pCurrent->m_fPosZ, vPath[j]->m_fPosX, vPath[j]->m_fPosZ));
                    DWORD dwWeight = max(DWORD(1), dwDistance);
                    if(dwPick < dwWeight)
                    {
                        bGoal = j;
                        break;
                    }
                    dwPick -= dwWeight;
                }
                m_bCurPathDir = BYTE(bGoal + 2);
            }

            if(bGoal > m_bCurPathID)
                m_bCurPathID++;
            else if(bGoal < m_bCurPathID)
                m_bCurPathID--;
            m_fStartX = m_fPosX;
            m_fStartY = m_fPosY;
            m_fStartZ = m_fPosZ;
        }

        LPTPATHPOINT pNext = vPath[m_bCurPathID];
        FLOAT fRad = FLOAT(rand() % 360) * FLOAT(M_PI) / 180.0f;
        fPosX = pNext->m_fPosX + pNext->m_fRadius * cosf(fRad);
        fPosY = pNext->m_fPosY;
        fPosZ = pNext->m_fPosZ + pNext->m_fRadius * sinf(fRad);
        bAction = rand() % 100 < 25 ? TA_RUN : TA_WALK;
        return TRUE;
    }

'''.replace("\n", "\r\n").replace("    ", "\t").encode("ascii")

path = ROOT / "TMonster.cpp"
data = path.read_bytes()
start = data.index(b"BYTE CTMonster::MoveNext(")
anchor = b"\tif(m_bMode != MT_GOHOME)\r\n"
index = data.index(anchor, start)
if data.count(b"Type 5 is reserved for ambient residents"):
    raise RuntimeError("Ambient branch already present")
path.write_bytes(data[:index] + route_branch + data[index:])
print("Ambient source patch applied")
