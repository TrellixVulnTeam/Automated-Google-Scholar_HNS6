import lib.logging as logging
LOG = logging.getLogger(__name__)

def main():
    from pathlib import Path
    output_dir = Path("./test_zoteroing")
    raw_dir = output_dir / "raw"

    if not output_dir.exists():
        output_dir.mkdir()

    if not raw_dir.exists():
        raw_dir.mkdir()

    for i in range(2):
        from lib.scraping._scraping_tracker import _scraping_tracker as ST
        st = ST(raw_dir)

        _page = i+1
        import lib.search.search_helper as SH
        urls = SH.search("test", page=_page)

        st.page(_page)
        st.page_begin()
        for url in urls:
            st.url(url)
            st.url_begin()

        import lib.zoteroing.Zoteroing_Helper as ZH
        ZH.start(urls, raw_dir)

        st.page_end()
        for url in urls:
            st.url(url)
            st.url_end()

    from lib.zoteroing._zoteroing_output_helper import _zoteroing_output_helper as ZOH
    zoh = ZOH(output_dir)
    zoh.manual_handling_file()
    zoh.assemble_zoteroing_output()

if __name__ == '__main__':
    import time
    start_time = time.time()

    main()

    LOG.debug(f"Time: --- {(time.time() - start_time)} seconds ---")