from nvitop import Device, ResourceMetricCollector
import pandas as pd

import os


class NvidiaTop():

    def __init__(self):
        self.cuda_available: bool = True
        self.device: Device | None = Device.all() if self.cuda_available else None
        self.resource_metric_collector: ResourceMetricCollector | None = ResourceMetricCollector() if self.cuda_available else None

        

    def get_resource_metrics_as_dict(self, cmd: str) -> dict[str, float]:
        """Measures the resource hardware CPU, GPU and MEM while executing the provided `cmd`.

        Parameters
        ----------
        cmd : str
            The command to be executed on the system that should be measured.

        Returns
        -------
        dict[str, float]
            Returns a dictionary with the resource metrics provided by `nvitop.ResourceMetricCollector`
        """
        metric_dict: [str, float] = dict()

        def cleanup_key(key: str) -> str:
            return key.removeprefix('<tag>/').replace(' ', '').replace('(%)', '').replace('(C)', '').replace('(W)', '').replace('(', '.').replace(')', '').replace('/', '.')

        with self.resource_metric_collector.context(tag='<tag>') as collector:
            os.system(cmd)
            collect_dict = collector.collect()

            metric_dict = {cleanup_key(k): v for k, v in collect_dict.items()}
            
        # TODO find a better way to properly reset the collector
        self.resource_metric_collector = ResourceMetricCollector() if self.cuda_available else None

        return metric_dict
    
    
    def get_resource_metric_as_dataframe(self, cmd: str) -> pd.DataFrame:
        """Measures the resource hardware CPU, GPU and MEM while executing the provided `cmd`.

        Parameters
        ----------
        cmd : str
            The command to be executed on the system that should be measured.

        Returns
        -------
        pandas Dataframe
            Returns a dataframe with the resource metrics provided by `nvitop.ResourceMetricCollector`
        """
        metric_dict = self.get_resource_metrics_as_dict(cmd=cmd)
        
        return pd.DataFrame.from_dict(metric_dict, orient='index').transpose()
    
    @staticmethod
    def merge_resource_metric_dfs(metric_results: list[pd.DataFrame], exclude_timestamps: bool = False) -> pd.DataFrame:
        """Merges resource metrics collected via this nvidia top class

        Parameters
        ----------
        metric_results : list[pd.DataFrame]
            A list of pandas dataframe elements that were collected via this class
        exclude_timestamps : bool, optional
            if `True` drops columns related to timestamps in order to omit duplicate data when using other monitoring tools, by default False

        Returns
        -------
        pd.DataFrame
            returns a Dataframe that consists of all resource metrics
        """
        concat_df = pd.concat(metric_results, ignore_index=True)
        
        if exclude_timestamps:
            concat_df.drop(['timestamp', 'last_timestamp'], axis=1)
        
        return concat_df
