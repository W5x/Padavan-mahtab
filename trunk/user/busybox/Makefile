SRC_NAME=busybox-1.35.0

all:
	$(MAKE) -j$(HOST_NCPU) -C $(SRC_NAME)

clean:
	$(MAKE) -C $(SRC_NAME) distclean

romfs:
	$(MAKE) -C $(SRC_NAME) CONFIG_PREFIX=$(ROMFSDIR) install

