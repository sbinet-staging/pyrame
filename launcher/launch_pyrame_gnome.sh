#DEBUGGER="gdb -ex run --args"
DEBUGGER=""
gnome-terminal --geometry=200x24   \
   --tab --title="VARMOD" \
--command="$DEBUGGER cmdmod /opt/pyrame/cmd_varmod.xml" \
   --tab --title="TCP" \
--command="$DEBUGGER cmdmod /opt/pyrame/cmd_tcp.xml" \
   --tab --title="SERIAL" \
--command="$DEBUGGER cmdmod /opt/pyrame/cmd_serial.xml" \
   --tab --title="RAWETH" \
--command="$DEBUGGER cmdmod /opt/pyrame/cmd_raweth.xml" \
   --tab --title="GPIB"    \
--command="$DEBUGGER cmdmod /opt/pyrame/cmd_gpib.xml" \
   --tab --title="PS"    \
--command="$DEBUGGER cmdmod /opt/pyrame/cmd_ps.xml" \
   --tab --title="AG_E3631A"    \
--command="$DEBUGGER cmdmod /opt/pyrame/cmd_ag_e3631a.xml" \
   --tab --title="AG_N6700B"    \
--command="$DEBUGGER cmdmod /opt/pyrame/cmd_ag_n6700b.xml" \
   --tab --title="LA_GEN8_90"    \
--command="$DEBUGGER cmdmod /opt/pyrame/cmd_la_gen8_90.xml" \
   --tab --title="HA_HMP4030"    \
--command="$DEBUGGER cmdmod /opt/pyrame/cmd_ha_hmp4030.xml" \
   --tab --title="CA_SY527"    \
--command="$DEBUGGER cmdmod /opt/pyrame/cmd_ca_sy527.xml" \
   --tab --title="KI_6487"    \
--command="$DEBUGGER cmdmod /opt/pyrame/cmd_ki_6487.xml" \
   --tab --title="MOTION"    \
--command="$DEBUGGER cmdmod /opt/pyrame/cmd_motion.xml" \
   --tab --title="NW_ESP301"    \
--command="$DEBUGGER cmdmod /opt/pyrame/cmd_nw_esp301.xml" \
   --tab --title="TH_APT" \
--command="$DEBUGGER cmdmod /opt/pyrame/cmd_th_apt.xml" \
   --tab --title="SG_WL350"    \
--command="$DEBUGGER cmdmod /opt/pyrame/cmd_sg_wl350.xml" \
   --tab --title="PATHS"    \
--command="$DEBUGGER cmdmod /opt/pyrame/cmd_paths.xml" \
   --tab --title="SIGNAL"    \
--command="$DEBUGGER cmdmod /opt/pyrame/cmd_signal.xml" \
   --tab --title="AG_33200"    \
--command="$DEBUGGER cmdmod /opt/pyrame/cmd_ag_33200.xml" \
   --tab --title="AG_33500"    \
--command="$DEBUGGER cmdmod /opt/pyrame/cmd_ag_33500.xml" \
   --tab --title="AG_81160"    \
--command="$DEBUGGER cmdmod /opt/pyrame/cmd_ag_81160.xml" \
   --tab --title="SIGPULSE"    \
--command="$DEBUGGER cmdmod /opt/pyrame/cmd_sigpulse.xml" \
   --tab --title="SIGSQUARE"    \
--command="$DEBUGGER cmdmod /opt/pyrame/cmd_sigsquare.xml" \
   --tab --title="LS_421"    \
--command="$debugger cmdmod /opt/pyrame/cmd_ls_421.xml" \
   --tab --title="DOMAIN"    \
--command="$DEBUGGER cmdmod /opt/pyrame/cmd_domain.xml" \
   --tab --title="OPERATOR"    \
--command="$DEBUGGER cmdmod /opt/pyrame/cmd_operator.xml" \
   --tab --title="DETECTOR"    \
--command="$DEBUGGER cmdmod /opt/pyrame/cmd_detector.xml" \
   --tab --title="CMOD"    \
--command="$DEBUGGER cmdmod /opt/pyrame/cmd_cmod.xml" \
   --tab --title="SKIROC" \
--command="$DEBUGGER cmdmod /opt/pyrame/cmd_skiroc.xml" \
   --tab --title="SPIROC" \
--command="$DEBUGGER cmdmod /opt/pyrame/cmd_spiroc.xml" \
   --tab --title="EASIROC" \
--command="$DEBUGGER cmdmod /opt/pyrame/cmd_easiroc.xml" \
   --tab --title="MAROC3" \
--command="$DEBUGGER cmdmod /opt/pyrame/cmd_maroc3.xml" \
   --tab --title="ACQCHAIN" \
--command="$DEBUGGER acq_server" \

